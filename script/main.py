import os
import logging
from WebScraping import WebScraping

if __name__ == '__main__':
    
    # Setup Log's File
    if not os.path.exists('Logs'):
        os.makedirs('Logs')
        
    logging.basicConfig( filename= 'Logs/logs_scraping_hm.txt',
                         level   = logging.INFO,
                         format  = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                         datefmt = '%Y-%m-%d %H:%M:%S')
    
    logger = logging.getLogger('WebScrapingH&M')
    
    # Web Scraping Application
    wb = WebScraping()
    
    data = wb.showroom_collect( logger )
    print('Still Working.')

    df1 = wb.collect_data( data, logger )
    print('Still Working..')
    
    df_clean = wb.data_cleaning( df1, logger )
    print('Still Working...')
    
    df_ref = wb.split_composition( df_clean, logger )

    df = wb.data_preparation( df_clean, df_ref, logger )
    
    wb.data_storange( df, logger )
    logger.info('[OK] Data Collected & Stored, check Database.')
    print('Done!')