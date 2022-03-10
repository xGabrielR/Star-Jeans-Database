import requests
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config( layout='wide', page_title="H&M Jeans Data", page_icon="💰" )

class HMDashboard():
    '''
    pre_html: Set the simple CSS & HTML on Page.
    load_dataset: Load Local SQLite Database.
    data_preparation: Prepare Datasets to feed the Dashboard.
    descriptive_statistical: First Visual Tables.
    simple_plots: Simple Plots based on Median.
    '''
    def __init__( self ):
        self.database_path = f'{cloud_url}'

    def pre_html( self ):
        html='''
        <style>
            * { padding: 1.5px; }
            p {color: #428df5; }
            ::selection { color: #b950ff; }
            h1 {color: #7033ff; text-align: center; }
            h2 {color: #8d5dfc}
        </style>
        '''
        st.markdown( html, unsafe_allow_html=True )

        return None

    def load_dataset( self ):
        r = requests.get( self.database_path, headers={'Content-type': 'application/json'} )
        df = pd.DataFrame( r.json(), columns=r.json()[0].keys() )

        return df

    def data_preparation( self, df ):
        n_att = df.select_dtypes( include=['float64', 'int64'] ).style.format("{:.2f}")
        c_att = df.select_dtypes( include=['object', 'datetime64[ns]'] )

        n_desc = df.select_dtypes( include=['float64', 'int64'] )
        c2 = pd.DataFrame( n_desc.apply( np.mean ) ).T
        c1 = pd.DataFrame( n_desc.apply( np.median ) ).T
        d1 = pd.DataFrame( n_desc.apply( np.std ) ).T
        d2 = pd.DataFrame( n_desc.apply( min ) ).T
        d3 = pd.DataFrame( n_desc.apply( max ) ).T
        d4 = pd.DataFrame( n_desc.apply( lambda x: x.max() - x.min() ) ).T

        n_desc = pd.concat( [d2, d3, d4, c1, c2, d1], axis=0 ).T.reset_index()
        n_desc.columns = ['att', 'min', 'max', 'range', 'median', 'mean', 'std']

        size_c = pd.DataFrame( c_att.groupby(['color']).size() / len(df) )
        size_f = pd.DataFrame( c_att.groupby(['fit']).size() / len(df) )

        data = {'numerical_att': n_att, 'categorical_att': c_att,
                'numerical_desc': n_desc, 'size_fit': size_f, 'size_color': size_c}

        return data

    def descriptive_statistical( self, data ):
        st.title('H&M Data Analysis')

        st.header('❒ Descriptive Statistical')

        c1, c2 = st.columns((2, 2))
        c1.subheader('Categorical Data')
        c2.subheader('Numerical Data')
        c1.dataframe( data['categorical_att'] )
        c2.dataframe( data['numerical_att'] )
        st.title('')

        c1, c2 = st.columns(2)
        c1.subheader('Numerical Data Description')
        c2.subheader('Percentage of Products Fit')
        c1.dataframe( data['numerical_desc'].style.format( {'min': '{:.2f}', 'max': '{:.2f}', 'mean': '{:.2f}', 'range': '{:.2f}', 'median': '{:.2f}', 'std': '{:.2f}'} ) )
        c2.dataframe( data['size_fit'].T.style.highlight_max(axis=1, color='#0b025c') )
        st.title('')

        st.subheader('Percentage of Products Colors')
        st.dataframe( data['size_color'].T.style.highlight_max(axis=1, color='#0b025c') )
        st.title(' ')

        return None

    def simple_plots( self, df ):
        st.header('❒ Visual Dataset on Plots')

        dfx = df[['date', 'price']].groupby('date').median().reset_index()
        fig = px.scatter(dfx, x='date', y='price', size='price', color_discrete_sequence=["white"], title='Median Price per Day', width=500, height=450)
        fig.update_layout( plot_bgcolor='#0e1117' )
        st.plotly_chart( fig, use_container_width=True )

        dfx = df[['fit', 'price']].groupby('fit').median().reset_index()
        fig = px.bar(dfx, x='fit', y='price', color_discrete_sequence=['navy'], title='Median Price per Fit', width=500, height=450)
        fig.update_layout( plot_bgcolor='#0e1117' )
        st.plotly_chart( fig, use_container_width=True )

        dfx = df[['color', 'price']].groupby('color').median().reset_index()
        fig = px.bar(dfx, x='color', y='price', color_discrete_sequence=['navy'], title='Median price per Color', width=500, height=450)
        fig.update_layout( plot_bgcolor='#0e1117' )
        st.plotly_chart( fig, use_container_width=True )

        return None

    def none_dataset( self ):
        st.title('H&M Data Analysis')

        st.subheader('Application Under Maintenance 😔')
        
        return None

if __name__ == '__main__':

    dash = HMDashboard()
    
    dash.pre_html()

    df = dash.load_dataset()

    if len(df.values.tolist()) == 0:
        dash.none_dataset()

    else:
        df1 = dash.data_preparation( df )

        dash.descriptive_statistical( df1 )

        dash.simple_plots( df )