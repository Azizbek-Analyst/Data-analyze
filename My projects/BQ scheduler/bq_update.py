# STEP 1 libraryes 
from google.cloud import bigquery_datatransfer
from google.cloud import bigquery
from google.protobuf.json_format import MessageToDict
import numpy as np
import pandas as pd
from pandas.io import gbq
import datetime as dt
import time


# Google Auth
import pydata_google_auth
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive',
]

credentials = pydata_google_auth.get_user_credentials(
    SCOPES,
    # Set auth_local_webserver to True to have a slightly more convienient
    # authorization flow. Note, this doesn't work if you're running from a
    # notebook on a remote sever, such as over SSH or with Google Colab.
    auth_local_webserver=True,
)



## STEP 2 ## 
def prior_week_end():
    '''You will get previous Monday'''
    if dt.datetime.now().isoweekday() == 7:
        return  dt.datetime.now() - dt.timedelta(days=((dt.datetime.now().isoweekday() - 1) % 7))
    else:
        return  dt.datetime.now() - dt.timedelta(days=((dt.datetime.now().isoweekday()) % 7))
 
def prior_week_start():
    '''You will get previous Sunday'''
    return prior_week_end() - dt.timedelta(days=6)


## STEP 3##
## Scheduled queries
def scheduled_queries(project_name= 'nothing'):
    ''' Enter your BigQuery project to receive all scheduled_queries'''
    if project_name == 'nothing':
        print('Please Enter your BigQuery project')
    else:
        try:
            client = bigquery_datatransfer.DataTransferServiceClient(credentials = credentials)
            parent = client.common_project_path(project_name)
            resp = client.list_transfer_configs(parent=parent)
            response_json = MessageToDict(resp._pb)
            data = []
            for k, v in response_json.items():
                for i in v:
                    if 'params' in i.keys():
                        if 'partitioning_field' in i['params'].keys():
                            data.append([i['destinationDatasetId'],i['params']['destination_table_name_template'], i['displayName'], i['params']['partitioning_field']])
            df_scheduled_queries = pd.DataFrame(data,columns=['Destination folder','Destination table','Scheduler name','Partition field'])
            display(df_scheduled_queries)
            return df_scheduled_queries
        except:
            print(f"Sorry! Resource {project_name} could not be found.")


## STEP 4 ##
def get_queries(destination_tables = 'nothing', project_name = 'nothing'):
    ''' 
    The function will allow you to get the last saved scheduled_queries from BigQuery
    1. Pre-enter the desired list of Destination tables Exp: ['events','sessions', 'etc']
    2. Enter your BigQuery project
    '''
    if destination_tables == 'nothing':
        print('Pre-enter the desired destination_tables')
    
    elif type(destination_tables) is str:
            destination_tables = [destination_tables]
            
    if project_name == 'nothing':
        print('Enter the desired Project name or Pre-create project variable Ex: project=\'your_bq_project\' ')
            
    else:
        all_queries_dic = {}
        try:
            
            client = bigquery_datatransfer.DataTransferServiceClient(credentials = credentials)
            parent = client.common_project_path(project_name) 
            resp = client.list_transfer_configs(parent=parent)
            response_json = MessageToDict(resp._pb)
            
            for k, v in response_json.items():
                for i in v:
                    if 'params' in i.keys():
                        if 'partitioning_field' in i['params'].keys():
                           if 'destination_table_name_template' in i['params'].keys():
                                    all_queries_dic[i['params']['destination_table_name_template']] = {
                                                                                                'full_path':i['destinationDatasetId'] +'.'+i['params']['destination_table_name_template'],
                                                                                                'params':{'partitioning_field':i['params']['partitioning_field']
                                                                                                          ,'query':i['params']['query']},
                                                                                                 'project_name': project_name}

            queries_dic = {}
            
            for i in destination_tables:
                if i in all_queries_dic.keys():
                    queries_dic[i] = all_queries_dic[i]
                    queries_dic[i]
               
                else:
                    print(f'{i.upper()} table not found in the {project_name}. \nYou can check the available tables with the function scheduled_queries("project_name")') 
            
            print(queries_dic.keys())
            
            return queries_dic  
        except:
            print(f"Sorry! Resource {project_name} could not be found in BigQuery.")


## STEP 5 ##
def update_destination_table(queries_dic,first_date,last_date, two_day_queries = None):
    
    process_time_start =  dt.datetime.now()
    query_total_bytes = 0
    
    '''
    Received scheduled_queries and dates allow you to update the necessary DataMarts
        1. queries_dic = Put a variable with the desired showcases and queries from the get_queries() function 
        2. first_date, last_daye = Put variables with start and end dates like \'2022-05-06\'
        3. two_day_queries = Put Queries with 2 day interval'''
    
    
    
    client = bigquery.Client(project = queries_dic[list(queries_dic.keys())[0]]['project_name'], credentials = credentials)

    for i in queries_dic.keys():
        query = f'''
              SELECT {queries_dic[i]['params']['partitioning_field']}
              FROM `{queries_dic[i]['project_name']}.{queries_dic[i]['full_path']}`
              WHERE {queries_dic[i]['params']['partitioning_field']} BETWEEN '{first_date}' AND '{last_date}'
              GROUP by 1
          '''
        
        ## OLD Подгрузка скриптов из файлов
        #with open(f'{i}.txt',) as f:
        #            read_file = f.read()
        #read_file = read_file.replace('@run_date', "'{run_date}'")

        
        ## Автоподгрузка из Шедулера BQ
        read_file = queries_dic[i]['params']['query'].replace('@run_date', "'{run_date}'")




       ## Даты проверки
        print(f'Checking the {i.upper()} data. For the period from {first_date} to {last_date}')

        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        
        # Start the query, passing in the extra configuration.
        query_job = client.query((query), job_config=job_config)  # Make an API request.
        
        #  Стоймость проверки.
        print("This query processed {:.2f} GB.".format(query_job.total_bytes_processed/1073741824))


        ## Подключение в BIQ
        df = gbq.read_gbq(query, project_id= queries_dic[i]['project_name'] )

        ## Создание фреймя для сравнения 
        date_index = df.set_index(df.columns[0])
        date_index.index = pd.to_datetime(date_index.index)


        ## Находим пустые даты
        missing_date = pd.date_range(start = first_date, end = last_date).difference(date_index.index)
        

        if missing_date.shape[0] > 0:
            for day in missing_date:
                
                print(f'I found a missed day {day}. I will upload it')
                start_time = dt.datetime.now()
                
                 ## Если интервал два дня
                if queries_dic[i]['full_path'] in two_day_queries:
                    missing_day = (day + dt.timedelta(days=2)).strftime('%Y-%m-%d')
                else:
                    missing_day = (day + dt.timedelta(days=1)).strftime('%Y-%m-%d')
                    
                       
                temp_sql = read_file.format(run_date = missing_day)


                # Load missing Data
                job_config = bigquery.QueryJobConfig(destination=f"{queries_dic[i]['project_name']}.{queries_dic[i]['full_path']}")
                job_config.write_disposition = 'WRITE_APPEND'  
                query_job = client.query(temp_sql, job_config=job_config) 




                # Status
                print(f"Query results loaded to the table {i.upper()}")
                query_job.result()
                if query_job.total_bytes_processed is not None:
                    print("This query processed {:.2f} GB.".format(query_job.total_bytes_processed/1073741824))
                query_total_bytes += query_job.total_bytes_processed
   
                print(f'Execution time >>> {dt.datetime.now() - start_time}\n')


        else:
            print(f'Table {i.upper()} has no missing values\n')
    
    # End        
    print('Process completed :)')
    print(f"Time spent  {dt.datetime.now() - process_time_start}")
    if query_total_bytes > 0:
        print("This query processed {:.2f} GB.".format(query_total_bytes/1073741824))