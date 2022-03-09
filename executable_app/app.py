import numpy as np
import pandas as pd
import PySimpleGUI as sg
from plots import PlotsHm
from sqlalchemy import create_engine

class HMApp():
    '''
    - prepare_data: Generate all Datasets used on app.
    - create_table: Create TKinter table on app.
    - table_layout: Window of search tables.
    - statistics_layout: Window of with Statistics functions;
    - plots_layout: Geral layout of all plots.
    - geral_window: First Window.
    '''
    def __init__( self ):
        self.con = create_engine( 'sqlite:///../script/h&m_datasets/h&m_database.sqlite' )
        self.df  = pd.read_sql_query( 'SELECT * FROM showroom', con=self.con )

    def prepare_dataset( self ):
        num_att = self.df.select_dtypes( include=['float64', 'int64'] )
        cat_att = self.df.select_dtypes( include=['object'] )

        size_c = pd.DataFrame( cat_att.groupby(['color']).size() / len(self.df) )
        size_f = pd.DataFrame( cat_att.groupby(['fit']).size() / len(self.df) )
        df_dat = self.df[['price', 'date']].groupby('date').median().reset_index()
        df_col = self.df[['price', 'color']].groupby('color').median().reset_index()
        df_fit = self.df[['price', 'fit']].groupby('fit').median().reset_index()

        c1 = pd.DataFrame( num_att.apply( np.mean ) ).T
        c2 = pd.DataFrame( num_att.apply( np.median ) ).T
        d1 = pd.DataFrame( num_att.apply( np.std ) ).T
        d2 = pd.DataFrame( num_att.apply( min ) ).T
        d3 = pd.DataFrame( num_att.apply( max ) ).T
        d4 = pd.DataFrame( num_att.apply( lambda x: x.max() - x.min() ) ).T

        m = pd.concat( [d2, d3, d4, c1, c2, d1,], axis=0 ).T.reset_index()
        m.columns = ['att', 'min', 'max', 'range', 'mean', 'median', 'std']
        m['mean'] = m['mean'].apply( lambda x: np.round( x, 2 ) )
        m['std']  = m['std'].apply( lambda x: np.round( x, 2 ) )

        data = {'num_desc': m, 'categorical_att': cat_att, 'numerical_att': num_att , \
                'size_color': size_c, 'size_fit': size_f, 'df_date': df_dat, 'df_color': df_col, 'df_fit': df_fit, 'df_raw': self.df }

        return data

    def create_table( self, data, head, title ):
        table = [[sg.Table( values=data,
                            headings=head,
                            font=('sans serif', 10),
                            justification='left',
                            pad=(25,25),
                            auto_size_columns=True,
                            num_rows=min(30, len(data)),
                            display_row_numbers=False )]]

        window = sg.Window( title, table, grab_anywhere=False )
        event, values = window.read()
        window.close()

        return None

    def table_layout( self ):
        layout_table = [[sg.Text('_'*30)],
                        [sg.Text(' ◮ Please, provide a Name')],
                        [sg.Text(' ◭ Or Blank for Full Dataset')],
                        [sg.Input(key='product_name')],
                        [sg.Button('Search')],
                        [sg.Text('_'*30)]]

        window_table = sg.Window( 'H&M - Table', layout_table, element_justification='c' )

        while True:
            event, values = window_table.read()

            if event == 'Search':
                product_name = values['product_name'].lower().replace(' ', '_')
                localize_product = df['df_raw'][df['df_raw']['name'].str.contains(product_name)]

                if localize_product.empty:
                    sg.popup('I dont finded this Product 🤔')

                else:
                    self.create_table( localize_product.values.tolist(), localize_product.columns.tolist(), 'H&M - Search Product' )

            if event == sg.WIN_CLOSED:
                break

        return None

    def statistics_layout( self ):
        layout_statistics = [[sg.Text('_'*30)],
                            [sg.Text(' ◮ Select How Feature Type you like to See')],
                            [sg.Button('Numerical Attributes'), sg.Button('Count Categorical Attributes')],
                            [sg.Text('_'*30)]]

        window_statistics = sg.Window( 'H&M - Statistics', layout_statistics, element_justification='c' )

        while True:
            event, values = window_statistics.read()

            if event == 'Numerical Attributes':
                self.create_table( df['num_desc'].values.tolist(), df['num_desc'].columns.tolist(), 'H&M - Numerical' )

            if event == 'Count Categorical Attributes':
                pl.plot_count_features( df['df_raw'] )

            if event == sg.WIN_CLOSED:
                break

        return None

    def plots_layout( self ):
        layout_plots = [[sg.Text('_'*30)],
                        [sg.Text(' ◮ Select How Graphic You like to See')],
                        [sg.Button('Median Price Per Day'), sg.Button('Fit & Color Price Median')],
                        [sg.Button('Median Price Per Fit'), sg.Button('Median Price Per Color'), sg.Button('Count per Features')],
                        [sg.Text('_'*30)]]

        window_plots = sg.Window( 'H&M - Plots', layout_plots, element_justification='c' )

        while True:
            event, values = window_plots.read()

            if event == 'Median Price Per Day':
                pl.plot_scatter_per_day( df['df_date'] )
        
            if event == 'Fit & Color Price Median':
                pl.plot_full_categorical( df['df_raw'], df['df_fit'], df['df_color'] )

            if event == 'Median Price Per Fit':
                pl.plot_price_per_fit( df['df_raw'], df['df_fit'] )

            if event == 'Median Price Per Color':
                pl.plot_price_per_color( df['df_raw'], df['df_color'] )

            if event == 'Count per Features':
                pl.plot_count_features( df['df_raw'] )

            if event == sg.WIN_CLOSED:
                break

        return None

    def geral_window( self ):
        default_layout = [[sg.Image('star.png', size=(400,225))],
                        [sg.Text('_'*30)],
                        [sg.Text('◈ H&M - Data Analysis')],
                        [sg.Text(' ')],
                        [sg.Button('Table'), sg.Button('Statistics'), sg.Button('Plots')], 
                        [sg.Text('_'*30)]]

        default_window = sg.Window( 'H&M - Dataset',  default_layout, element_justification='c' )

        while True:
            event, values = default_window.read()

            if event == 'Table':
                self.table_layout()

            if event == 'Statistics':
                self.statistics_layout()
            
            if event == 'Plots':
                self.plots_layout()

            if event == sg.WIN_CLOSED:
                break

        return None

if __name__ == '__main__':

    pl  = PlotsHm()
    app = HMApp()

    sg.theme('Black')

    df = app.prepare_dataset()

    app.geral_window()