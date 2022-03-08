import os
import re
import logging
import requests
import numpy  as np
import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import create_engine

class WebScraping():
    '''
    showroom_collect: Collect first 36 Products of M&M Website.
    collect_data: Collect all products colors and individual products composition.
    data_cleaning: Clean the Dataset after Collect.
    split_composition: Split Composition feature in unique composition features.
    data_preparation: Prepare Final Dataset with unique composition and detailed features.
    data_storange: Save pandas dataset on SQLite Database.
    '''

    def __init__( self ):
        self.url = 'https://www2.hm.com/en_us/men/products/jeans.html'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5),AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        self.database = 'sqlite:///h&m_datasets/h&m_database.sqlite'
        
    def showroom_collect( self, logger ):
        page = requests.get( self.url, headers=self.headers )
        soup = BeautifulSoup( page.text, 'html.parser' )

        products = soup.find( 'ul', class_='products-listing small' )
        products_list = products.find_all( 'article', class_='hm-product-item' )
        p_code = [p.get('data-articlecode') for p in products_list]

        p_type = [p.get('data-category') for p in products_list]
        products_list = products.find_all( 'a', class_='link' )
        p_name = [p.get_text() for p in products_list]

        data = pd.DataFrame([p_code, p_name, p_type]).T

        try:
            data = pd.DataFrame([p_code, p_name, p_type]).T
            data.columns = ['code', 'name', 'category']

        except ValueError:
            logger.error('[ERROR] Cannot Create Dataframe at showroom_collect.')

        return data

    def collect_data( self, data, logger ):
        df1 = pd.DataFrame()

        for ic in data.code.tolist(): # Colors Collect
            url = 'https://www2.hm.com/en_us/productpage.'+ ic +'.html'
            page = requests.get( url, headers=self.headers )
            soup = BeautifulSoup( page.text, 'html.parser' )

            products_list = soup.find_all( 'a', class_='filter-option miniature' ) + soup.find_all( 'a', class_='filter-option miniature active' )
            p_colors = [p.get( 'data-color' ) for p in products_list]
            p_articlecode = [p.get( 'data-articlecode' ) for p in products_list]

            try:
                df_color = pd.DataFrame( [p_articlecode, p_colors] ).T
                df_color.columns = ['Art. No.', 'color']

            except ValueError:
                logger.error('[ERROR] Cannot Create Colors Dataframe at collect_data')

            for ip in range( len( df_color ) ): # Individual Product Colors Dataset
                url = 'https://www2.hm.com/en_us/productpage.' + df_color['Art. No.'][ip] + '.html'
                page = requests.get( url, headers=self.headers )

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
                    try:
                        df = df.drop( columns=['Care instructions'], axis=1 )

                        df = df.drop_duplicates()

                        df1 = pd.concat( [df1, df], axis=0 )

                    except ValueError:
                        logger.error('[ERROR] Cannot Create Full Dataframe at collect_data.')

        return df1

    def data_cleaning( self, df, logger ):
        df = df.drop_duplicates()

        df = df.iloc[:, 2:]

        if 'Size' in df.columns:
            df = df.drop( columns=['Material', 'Imported', 'Concept', 'Nice to know', 'messages.clothingStyle', 'More sustainable materials', 'Size'], axis=1 )

        else:
            df = df.drop( columns=['Material', 'Imported', 'Concept', 'Nice to know', 'messages.clothingStyle', 'More sustainable materials'], axis=1 )

        b = df.iloc[3:, :]
        a = df.iloc[:2, :]
        df = pd.concat( [b, a], axis=0 )

        try:
            df.columns = ['fit', 'composition', 'color', 'product_id', 'price']

            df = df.fillna( method='ffill' )

            df = df[~df['color'].str.contains('Solid-')]

            df = df.reset_index( drop=True )

            df.fit = [f.lower().replace(' ', '_') for f in df.fit]
            df.color = [f.lower().replace(' ', '_') for f in df.color]

            for j in ['Pocket lining: ', 'Shell: ', 'Lining: ', 'Pocket: ']:
                df.composition = [ic.strip() for ic in df.composition.str.replace(j, '')]

        except ValueError:
            logger.error('[ERROR] Cannot Clean Dataframe at data_cleaning.')

        return df

    def split_composition( self, df, logger ):
        df_ref = pd.DataFrame( index=range( len( df ) ), columns=['cotton_', 'polyester_', 'spandex_', 'elasterell_'] )

        try:
            df3 = df.composition.str.split(',', expand=True).reset_index(drop=True)

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

        except ValueError:
            logger.error('[ERROR] Cannot Create Composition Dataframe at split_composition.')

        for f in df_ref.columns.tolist():
            df_ref[f] = df_ref[f].fillna(f.title() + ' 0%')
            df_ref[f] = df_ref[f].apply( lambda x: int(re.search('\d+', x).group(0))/100 )

        return df_ref

    def data_preparation( self, df_clean, df_ref, logger ):
        try:
            df = pd.concat( [df_clean, df_ref], axis=1 )
            df = df.drop( columns=['composition'], axis=1 )

            df['date'] = datetime.now().strftime("%Y-%m-%d")

            df = df[['product_id', 'color', 'fit', 'price', 'cotton', 'polyester', 'spandex', 'elasterell', 'date']]

        except ValueError:
            logger.error('[ERROR] Cannot Create a Complete Dataset.')

        return df

    def data_storange( self, df, logger ):
        try:
            con = create_engine(self.database)

            df.to_sql( 'showroom', con=con, index=False, if_exists='append' )

            df.to_csv('h&m_datasets/h&m_' + df['date'][0])

        except ValueError:
            logger.error('[ERROR] Cannot Store Dataset at Database on data_storange.')

        return None
