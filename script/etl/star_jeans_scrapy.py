import re
import json
import requests
import pandas as pd
from pandas.core.frame import DataFrame

from sys import stdout
from time import sleep
from bs4  import BeautifulSoup
from datetime import datetime
from sqlalchemy import create_engine

from utils import BasePipeline
from utils import DB_NAME,DB_HOST,DB_PASS,DB_USER,DB_PORT

CURRENT_DATETIME = datetime.now().strftime("%Y-%m-%d")

class WebScrapingStarJeans(BasePipeline):
    def __init__(self):
        self.url = 'https://www2.hm.com/en_us/men/products/jeans.html'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5),AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    def showroom_collect(self, **context) -> DataFrame:
        page = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        products = soup.find('ul', class_='products-listing small')

        products_list = products.find_all( 'article', class_='hm-product-item' )
        p_code = [p.get('data-articlecode') for p in products_list]
        p_type = [p.get('data-category') for p in products_list]

        products_list = products.find_all( 'a', class_='link' )
        p_name = [p.get_text() for p in products_list]

        products_list = products.find_all( 'span', class_='price regular' )
        p_price = [p.get_text() for p in products_list]
        p_price = [float(p.replace('$ ', '')) for p in p_price]

        data = pd.DataFrame([p_code, p_name, p_type, p_price]).T
        data.columns = ['code', 'name', 'category', 'price']

        data = json.dumps(data.to_dict(orient='records'))

        context['ti'].xcom_push(key='show_data', value=data)

    def unique_colors_collect(self, code_index):
        url = 'https://www2.hm.com/en_us/productpage.'+ code_index +'.html'
        page = requests.get( url, headers=self.headers )
        soup = BeautifulSoup( page.text, 'html.parser' )

        products_list = soup.find_all( 'a', class_='filter-option miniature' ) + soup.find_all( 'a', class_='filter-option miniature active' )
        p_colors = [p.get( 'data-color' ) for p in products_list]

        p_articlecode = [p.get( 'data-articlecode' ) for p in products_list]

        df_color = pd.DataFrame( [p_articlecode, p_colors] ).T
        df_color.columns = ['Art. No.', 'color']
        
        return df_color
        
    def individual_colors_collect(self, df1, df_color, color_index):
        url = 'https://www2.hm.com/en_us/productpage.' + df_color['Art. No.'][color_index] + '.html'
        page = requests.get( url, headers=self.headers )
        sleep(.5)

        soup = BeautifulSoup( page.text, 'html.parser' ) # HTML With Soup
        p = [list(filter(None, x.get_text().split('\n'))) for x in soup.find_all('div','details-attributes-list-item')]
        price = [float(p.get_text().strip().replace('$', '')) for p in soup.find_all('span', 'price-value')]
        p = p+[['Price', price[0]]]
        
        df = pd.DataFrame( p ).T
        df.columns = df.iloc[0, :]
        df = df.iloc[1:, :]

        if not 'Care instructions' in df.columns.tolist():
            pass

        else:
            df = df.drop( columns=['Care instructions'], axis=1 )

            df = df.drop_duplicates()

            df1 = pd.concat( [df1, df], axis=0 )
            
            return df1

    def get_all_dataset(self, **context):
        data = context['ti'].xcom_pull(key='show_data')
        data = pd.DataFrame(json.loads(data))
        
        df1 = pd.DataFrame()
        
        for ic in data.code.tolist():
            stdout.write(f"Workign at -> {ic}")
            stdout.flush()
            df_color = self.unique_colors_collect(ic)
            
            for ip in range( len( df_color ) ): # Individual Product Colors Dataset
                try:
                    df1 = self.individual_colors_collect(df1, df_color, ip)
                except:
                    print(f'Erro no produto: {ic}!!!')
                    
                    missing_collect = data.iloc[data.code[data.code.str.contains(ic)].index[0]:, :]
                    
                    df1.to_csv(f'total_dataset_{CURRENT_DATETIME}.csv')
                    missing_collect.to_csv(f'missing_colors_{CURRENT_DATETIME}.csv')

                    df1 = json.dumps(df1.to_dict(orient='records'))
                    context['ti'].xcom_push(key='not_full_dataset', value=df1)
                    
                    return 'not_full_dataset'
        
        df1 = json.dumps(df1.to_dict(orient='records'))
        context['ti'].xcom_push(key='full_dataset', value=df1)

        return 'full_dataset'


    # Dataset Cleaning

    def first_clean(self, df):
        df2 = df.drop_duplicates()

        df2 = df2.iloc[:, 2:]

        if 'Size' in df2.columns:
            df2 = df2.drop( columns=['Material', 'Imported', 'Concept', 'Nice to know', 'messages.clothingStyle', 'More sustainable materials', 'Size'], axis=1 )
            
        else:
            df2 = df2.drop( columns=['Material', 'Imported', 'Concept', 'Nice to know', 'messages.clothingStyle', 'More sustainable materials'], axis=1 )

        dfx = df2.iloc[3:, :]
        a = df2.iloc[:2, :]
        df2 = pd.concat( [dfx, a], axis=0 )

        if 'Collection' in df2.columns:
            df2 = df2.drop("Collection", axis=1)

        df2.columns = ['fit', 'composition', 'color', 'product_id', 'price']

        df2 = df2.fillna( method='ffill' )
        df2 = df2.iloc[1:, :]   ##### Update 01/04/2022

        df2 = df2[~df2['color'].str.contains('Solid-')]

        df2 = df2.reset_index( drop=True )

        df2.fit = [f.lower().replace(' ', '_') for f in df2.fit]
        df2.color = [f.lower().replace(' ', '_') for f in df2.color]

        for j in ['Pocket lining: ', 'Shell: ', 'Lining: ', 'Pocket: ']:
            df2.composition = [ic.strip() for ic in df2.composition.str.replace(j, '')]

        return df2
        

    def composition_clean(self, df2):
        df_ref = pd.DataFrame( index=range( len( df2 ) ), columns=['cotton_', 'polyester_', 'spandex_', 'elasterell_'] )

        df3 = df2.composition.str.split(',', expand=True).reset_index(drop=True)

        if df3.shape[1] >= 3:
            df_cot0 = df3.loc[df3[0].str.contains('Cotton', na=True ), 0] # Need a For Loop on This.
            df_cot1 = df3.loc[df3[1].str.contains('Cotton', na=True ), 1]
            df_cot0.name, df_cot1.name = ['cotton', 'cotton']

            df_cott = df_cot0.combine_first( df_cot1 )
            df_ref = pd.concat( [df_ref, df_cott], axis=1 ).drop( columns=['cotton_'], axis=1 )

            df_poly0 = df3.loc[df3[0].str.contains('Polyester', na=True), 0]
            df_poly1 = df3.loc[df3[1].str.contains('Polyester', na=True), 1]
            df_poly0.name, df_poly1.name = ['polyester']*2

            df_poly = df_poly0.combine_first( df_poly1 )
            df_ref = pd.concat( [df_ref, df_poly], axis=1 ).drop( columns=['polyester_'], axis=1 )

            df_sp0 = df3.loc[df3[1].str.contains('Spandex', na=True), 1]
            df_sp1 = df3.loc[df3[2].str.contains('Spandex', na=True), 2]
            df_sp0.name, df_sp1.name = ['spandex']*2

            df_sp = df_sp0.combine_first( df_sp1 )
            df_ref = pd.concat( [df_ref, df_sp], axis=1 ).drop( columns=['spandex_'], axis=1 )

            df_el = df3.loc[df3[1].str.contains('Elasterell', na=True), 1]
            df_el.name = 'elasterell'

            df_ref = pd.concat( [df_ref, df_el], axis=1 ).drop( columns=['elasterell_'], axis=1 )

            for f in df_ref.columns.tolist():
                df_ref[f] = df_ref[f].fillna(f.title() + ' 0%')
                df_ref[f] = df_ref[f].apply( lambda x: int(re.search('\d+', x).group(0))/100 )
            
            return df_ref

        else:
            df_cot0 = df3.loc[df3[0].str.contains('Cotton', na=True ), 0] # Need a For Loop on This.
            df_cot1 = df3.loc[df3[1].str.contains('Cotton', na=True ), 1]
            df_cot0.name, df_cot1.name = ['cotton', 'cotton']

            df_cott = df_cot0.combine_first( df_cot1 )
            df_ref = pd.concat( [df_ref, df_cott], axis=1 ).drop( columns=['cotton_'], axis=1 )

            df_poly0 = df3.loc[df3[0].str.contains('Polyester', na=True), 0]
            df_poly1 = df3.loc[df3[1].str.contains('Polyester', na=True), 1]
            df_poly0.name, df_poly1.name = ['polyester']*2

            df_poly = df_poly0.combine_first( df_poly1 )
            df_ref = pd.concat( [df_ref, df_poly], axis=1 ).drop( columns=['polyester_'], axis=1 )

            for f in df_ref.columns.tolist():
                df_ref[f] = df_ref[f].fillna(f.title() + ' 0%')
                df_ref[f] = df_ref[f].apply( lambda x: int(re.search('\d+', x).group(0))/100 )
            
            return df_ref

    def merge_dataset(self, df, df_ref):
        df_clean = pd.concat( [df, df_ref], axis=1 )
        df_clean = df_clean.drop( columns=['composition'], axis=1 )

        df_clean['date'] = datetime.now().strftime("%Y-%m-%d")
        df_clean['name'] = df_clean['fit'].apply( lambda x: x.replace('fit', 'jeans'))

        df_clean = df_clean[['product_id', 'name', 'color', 'fit', 'price', 'cotton', 'polyester', 'spandex', 'elasterell', 'date']]

        return df_clean

    def clean_dataset(self, **context):
        df = 'checking'
        try:
            df = context['ti'].xcom_pull(key='full_dataset')
        except:
            print('Missing DF')

        if not type(df).__name__ == 'DataFrame':
            df = context['ti'].xcom_pull(key='full_dataset')

        df = pd.DataFrame(json.loads(df))
        
        df = self.first_clean(df)

        df = json.dumps(df.to_dict(orient='records'))
        context['ti'].xcom_push(key='clean_dataset', value=df)


    def complete_clean_data(self, **context):
        df = context['ti'].xcom_pull(key='clean_dataset')
        df = pd.DataFrame(json.loads(df))

        df_ref = self.composition_clean(df)

        df_clean = self.merge_dataset(df, df_ref)

        df_clean = json.dumps(df_clean.to_dict(orient='records'))
        context['ti'].xcom_push(key='complete_clean_dataset', value=df_clean)


    def data_store(self, **context):
        df = context['ti'].xcom_pull(key='complete_clean_dataset')
        df = pd.DataFrame(json.loads(df))
        
        db = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        con = db.connect()

        df.to_sql('showroom', con=con, index=False, if_exists='append')
        
        con.close()

        return None

if __name__ == '__main__':
    wb = WebScrapingStarJeans()
    print(f'\n\nStarted at {CURRENT_DATETIME}')

    showroom_dataset = wb.showroom_collect()
    
    full_dataset = wb.get_all_dataset(showroom_dataset)
    
    df_cleaned = wb.clean_dataset(full_dataset)

    complete_dataset = wb.complete_clean_data(df_cleaned)
    
    wb.data_store(complete_dataset)
    print(f"\n\nEnded at {datetime.now().strftime('%Y-%m-%d')}")