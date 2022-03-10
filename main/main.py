import os
import time
import logging
import pyautogui as pa
from datetime import datetime
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

    date = datetime.now().strftime('%Y_%m_%d')
    if (not df.empty) & (df.columns.tolist() == ['product_id', 'name', 'color', 'fit', 'price', 'cotton', 'polyester', 'spandex', 'elasterell', 'date']):
        for tm, cmd in zip( [3]*3, ['git add *', f'git commit -m "Auto Commit -> {date}"', 'git push heroku master'] ):
            os.system(cmd)
            time.sleep(tm)