import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine 

plt.rcParams['figure.figsize'] = [15, 6]
plt.rcParams['font.size'] = 7

class PlotsHm():
    def __init__( self ):
        self.database_path = 'sqlite:///../script/h&m_datasets/h&m_database.sqlite'
        self.palette=sns.diverging_palette(359, 359, n=5, s=999, l=50, center='dark')

    def args_b( self, color=(1, 1, 1, 0), edgecolor=['blue', 'red'], linewidth=2 ):
        return {'linewidth': linewidth, 'color': color, 'edgecolor': edgecolor }

    def data_preparation( self ):
        con = create_engine( self.database_path )
        df = pd.read_sql_query( 'SELECT * FROM showroom', con=con )
        df_dat = df[['price', 'date']].groupby('date').median().reset_index()
        df_col = df[['price', 'color']].groupby('color').median().reset_index()
        df_fit = df[['price', 'fit']].groupby('fit').median().reset_index()

        data = {'df_raw': df, 'df_date': df_dat, 'df_color': df_col, 'df_fit': df_fit}

        return data

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