import requests
import smtplib
import email.message
import numpy as np
import pandas as pd
import seaborn as sns
import PySimpleGUI as sg
from datetime import datetime
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [15, 6]
plt.rcParams['font.size'] = 7

class HMApp():

    def send_email( self ):
        msg_email = 'ERROR at | ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' | , check Heroku Logs to find the Error.'
        sender_email = f'{secret_email}'
        sender_pass  = f'{secret_pass}'
        receiver_email = f'{secret_receiver}'

        msg = email.message.Message()
        msg['From'] = sender_email
        msg['To']   = receiver_email
        msg['Subject'] = 'Status Coleta de Dados H&M'
        msg.set_payload( msg_email )

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login( sender_email, sender_pass)
        text = msg.as_string()
        session.sendmail( sender_email, receiver_email, text)
        session.quit()
        return None
    
    def prepare_dataset( self ):
        try:
            r = requests.get( f'{cloud_url}', headers={'Content-type': 'application/json'} )
        
        except ValueError:
            print('Error')

        if not r.status_code == 200:
            self.send_email()

        else:
            df = pd.DataFrame( r.json(), columns=r.json()[0].keys() )
            num_att = df.select_dtypes( include=['float64', 'int64'] )
            cat_att = df.select_dtypes( include=['object'] )

            size_c = pd.DataFrame( cat_att.groupby(['color']).size() / len(df) )
            size_f = pd.DataFrame( cat_att.groupby(['fit']).size() / len(df) )
            df_dat = df[['price', 'date']].groupby('date').median().reset_index()
            df_col = df[['price', 'color']].groupby('color').median().reset_index()
            df_fit = df[['price', 'fit']].groupby('fit').median().reset_index()

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
                    'size_color': size_c, 'size_fit': size_f, 'df_date': df_dat, 'df_color': df_col, 'df_fit': df_fit, 'df_raw': df }

            return data

        return None

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
                self.plot_count_features( df['df_raw'] )

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
                self.plot_scatter_per_day( df['df_date'] )
        
            if event == 'Fit & Color Price Median':
                self.plot_full_categorical( df['df_raw'], df['df_fit'], df['df_color'] )

            if event == 'Median Price Per Fit':
                self.plot_price_per_fit( df['df_raw'], df['df_fit'] )

            if event == 'Median Price Per Color':
                self.plot_price_per_color( df['df_raw'], df['df_color'] )

            if event == 'Count per Features':
                self.plot_count_features( df['df_raw'] )

            if event == sg.WIN_CLOSED:
                break

        return None

    def geral_window( self, data ):
        if data == None:
            default_layout = [[sg.Image('.img\\star.png', size=(400,255))],
                              [sg.Text('_'*30)],
                              [sg.Text('App Under Maintenance  ._.) b')],
                              [sg.Button('Exit')],
                              [sg.Text('_'*30)]]

            default_window = sg.Window( 'H&M - Dataset', default_layout, element_justification='c' )

            while True:
                event, values = default_window.read()
                
                if event == 'Exit':
                    break

                if event == sg.WIN_CLOSED:
                    break

        else:
            default_layout = [[sg.Image('.img\\star.png', size=(400,225))],
                            [sg.Text('▃▃▃▃▃▃ ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃\n\n▃   ◈ H&M - Data Analysis\n▃   ▃▃▃▃▃▃ ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃')], 
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

    def args_b( self, color=(1, 1, 1, 0), edgecolor=['blue', 'red'], linewidth=2 ):
        return {'linewidth': linewidth, 'color': color, 'edgecolor': edgecolor }

    def plot_count_features( self, df_raw ):
        fig, ax = plt.subplots( 1, 2, figsize=(10, 5))
        ax = ax.flatten()
        sns.countplot( y=df_raw['fit'], ax=ax[0], **self.args_b(edgecolor=['blue']))
        sns.countplot( y=df_raw['color'], ax=ax[1], **self.args_b(edgecolor=['red'] ) )
        ax[0].set_title('Count per Fit')
        ax[1].set_title('Cout per Color')
        plt.tight_layout()
        plt.show()
        
        return None

    def plot_scatter_per_day( self, df_date ):
        fig, ax = plt.subplots( figsize=(5, 5) )
        ax.scatter( df_date['date'], df_date['price'], c='r' )
        ax.set_title('Median Price per Day')
        ax.set_xlabel('date')
        ax.set_ylabel('price')
        plt.show()

        return None

    def plot_price_per_fit( self, df_raw, df_fit ):
        fig, ax = plt.subplots( 1, 2, figsize=(10, 5))
        ax = ax.flatten()
        ax[0].barh( df_fit['fit'], df_fit['price'], **self.args_b(edgecolor=['blue'] ) )
        sns.countplot( y=df_raw['fit'], ax=ax[1], **self.args_b(edgecolor=['red'] ) )
        ax[0].set_title('Median per fit')
        ax[1].set_title('Cout per fit')
        ax[0].set_xlabel('price')
        ax[0].set_ylabel('fit')
        plt.tight_layout()
        plt.show()

        return None

    def plot_price_per_color( self, df_raw, df_col ):
        fig, ax = plt.subplots( 1, 2, figsize=(10, 5))
        ax = ax.flatten()
        ax[0].barh( df_col['color'], df_col['price'], **self.args_b(edgecolor=['blue'] ) )
        sns.countplot( y=df_raw['color'], ax=ax[1], **self.args_b(edgecolor=['red'] ) )
        ax[0].set_title('Median per color')
        ax[1].set_title('Cout per color')
        ax[0].set_xlabel('price')
        ax[0].set_ylabel('color')
        plt.tight_layout()
        plt.show()

        return None

    def plot_full_categorical( self, df_raw, df_fit, df_col ):
        fig, ax = plt.subplots( 2, 2, figsize=(10, 5))
        ax = ax.flatten()
        ax[0].barh( df_fit['fit'], df_fit['price'], **self.args_b(edgecolor=['blue'] ) )
        ax[2].barh( df_col['color'], df_col['price'], **self.args_b(edgecolor=['blue'] ) )
        sns.countplot( y=df_raw['fit'], ax=ax[1], **self.args_b(edgecolor=['red']) )
        sns.countplot( y=df_raw['color'], ax=ax[3], **self.args_b(edgecolor=['red']) )
        for k in zip( range( 0, 4 ), ['Median per fit', 'Cout per fit', 'Median per Color', 'Cout per Color']):
            ax[k[0]].set_title(k[1])
            if k[0] == 1 or k[0] == 3: continue
            ax[k[0]].set_xlabel('price')
        ax[0].set_ylabel('fit')
        ax[2].set_ylabel('color')
        plt.tight_layout()
        plt.tight_layout()
        plt.show()

        return None

if __name__ == '__main__':

    app = HMApp()

    sg.theme('Black')

    df = app.prepare_dataset()

    app.geral_window( df )