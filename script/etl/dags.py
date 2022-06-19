from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

from datetime import datetime, timedelta
from star_jeans_scrapy import WebScrapingStarJeans

pipeline = WebScrapingStarJeans()

DEFAULT_ARGS = {
    'retries': 2,
    'owner': 'airflow',
    'email_on_retry': False,
    'email_on_falure': False,
    'start_date': datetime(2022, 6, 18),
    'retry_delay': timedelta(minutes=5) 
}

dag = DAG(
    'WebScrapingStarJeans',
    description='Web Scraping of H&M Daily to Postgresql',
    catchup=False,
    schedule_interval='@daily',
    default_args=DEFAULT_ARGS,
)

showroom_collect_task = PythonOperator(
    task_id='showroom_collect',
    python_callable=pipeline.showroom_collect,
    provide_context=True,
    dag=dag
)

get_scrapy_results_task = BranchPythonOperator(
    task_id='get_scrapy_results',
    python_callable=pipeline.get_all_dataset,
    provide_context=True,
    dag=dag
)

not_full_dataset_task = DummyOperator(
    task_id='not_full_dataset',
    dag=dag
)

full_dataset_task = DummyOperator(
    task_id='full_dataset',
    dag=dag
)

clean_dataset_task = PythonOperator(
    task_id='clean_scrapy_dataset',
    python_callable=pipeline.clean_dataset,
    trigger_rule='none_failed_or_skipped',
    provide_context=True,
    dag=dag 
)

complete_clean_data_task = PythonOperator(
    task_id='complete_clean_data',
    python_callable=pipeline.complete_clean_data,
    provide_context=True,
    dag=dag
)

store_dataset_task = PythonOperator(
    task_id='store_dataset_on_postgresql',
    python_callable=pipeline.data_store,
    provide_context=True,
    dag=dag
)

showroom_collect_task >> get_scrapy_results_task >> [full_dataset_task, not_full_dataset_task] >>  clean_dataset_task >> complete_clean_data_task >> store_dataset_task