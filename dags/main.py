from datetime import datetime, timedelta
import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from ..plugins.helpers import SqlQueries
from ..plugins.operators import StageToRedshiftOperator, LoadFactOperator, LoadDimensionOperator, DataQualityOperator



default_args = {
    'owner': 'Tomas Baidal',
    'start_date': pendulum.now(), 
    'depends_on_past': False,
    'retries': 3,  
    'retry_delay': timedelta(minutes=2),
    'catchup_by_default': False,
    'email_on_retry': False
}

dag = DAG(
    'final_project',
    default_args=default_args,
    description='Load and transform data in Redshift using Airflow',
    schedule_interval='@hourly' 
)

my_s3_bucket = "tomas-airflow-udacity"

start_operator = EmptyOperator(task_id='Begin_execution', dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    table="staging_events",
    s3_bucket=my_s3_bucket,
    s3_key="log-data",
    data_format="JSON 'auto'"
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    table="staging_songs",
    s3_bucket=my_s3_bucket,
    s3_key="song-data",
    data_format="JSON 'auto'"
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id="redshift",
    table="songplays",
    sql_query=SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table="users",
    sql_query=SqlQueries.user_table_insert,
    is_append_only=False
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table="songs",
    sql_query=SqlQueries.song_table_insert,
    is_append_only=False
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table="artists",
    sql_query=SqlQueries.artist_table_insert,
    is_append_only=False
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table="time",
    sql_query=SqlQueries.time_table_insert,
    is_append_only=False
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    tables=["songplays", "users", "songs", "artists", "time"]
)

end_operator = EmptyOperator(task_id='Stop_execution', dag=dag)

start_operator >> [stage_events_to_redshift, stage_songs_to_redshift] >> load_songplays_table
load_songplays_table >> [load_user_dimension_table, load_song_dimension_table, load_artist_dimension_table, load_time_dimension_table] >> run_quality_checks
run_quality_checks >> end_operator






