# Databricks notebook source
#Where to place Config File in Hive
#Hive/Jhub
#/home/derek mk tsui/Hive_test_script_prod/AdvancedStats_Config.csv

#ADLS
#wandisco/Test_Validation/Advanced_Statistics/AdvancedStats_Config.csv

#Hive folder overwriting 
#/home/derek mk tsui/Hive_test_script_prod/Hive_tablename_metadata_count.csv
#/home/derek mk tsui/Hive_test_script_prod/Hive_tablename_cat.csv
#/home/derek mk tsui/Hive_test_script_prod/Hive_tablename_num.csv
#/home/derek mk tsui/Hive_test_script_prod/Hive_tablename_date.csv

#ADLS
#wandisco/Test_Validation/Advanced_Statistics/yyyyMMdd/All50tablesHive,Adls,CompareMetrics.

# COMMAND ----------

# Import libraries
import pandas as pd
import numpy as np
import datetime as dt
import time
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import *
from timeit import default_timer as timer
import os
from pyhive import hive


########################################################################################################################
#input params:
    
    #db schema
# db_nm = "kh_published_cas_db"
#     #table names
# tbl_list = [
#             'tais_uw_data'
#             ]
#     #primary keys for each table
# primary_key_list = [
#                     "pol_num"
#                    ]

    #exportpath in JHub
export_path = '/home/derek mk tsui/Hive_test_script_prod/'
######################################################################################################################
#Hive settings
# spark = SparkSession.builder.master("yarn")\
#         .appName("timezn-check")\
#         .config("spark.sql.session.timeZone", "UTC")\
#         .config('spark.jars', '/usr/hdp/current/hive_warehouse_connector/hive-warehouse-connector-assembly-1.0.0.3.1.4.100-4.jar')\
#         .config('spark.submit.pyFiles', '/usr/hdp/current/hive_warehouse_connector/pyspark_hwc-1.0.0.3.1.4.100-4.zip')\
#         .config('spark.security.credentials.hiveserver2.enabled', 'false')\
#         .config('spark.port.maxRetries', '50')\
#         .enableHiveSupport().getOrCreate()

spark = SparkSession.builder.master("local[*]").appName("timezn-check").appName("<app-name>").enableHiveSupport().getOrCreate()

from pyspark_llap.sql.session import HiveWarehouseSession
hiveWH = HiveWarehouseSession.session(spark).build()

# spark.conf.set("spark.sql.shuffle.partitions", 10)
spark.conf.set("spark.sql.shuffle.partitions", "5")
spark.conf.set("spark.default.parallelism", "5")

# connect to edl
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

# conn = hive.connect(host='azalvedlmstdp01.p01eaedl.manulife.com',
#     port=10000,
#     database='default',
#     auth='KERBEROS',
#     kerberos_service_name='hive')
# cursor = conn.cursor()

#Create spark configuration object
conf = SparkConf()
conf.setMaster("local").setAppName("My app")


#Create spark context and sparksession
sc = SparkContext.getOrCreate(conf=conf)
spark = SparkSession(sc)

# COMMAND ----------

# 1. check primary key

def check_primary_key(prim_key, db_nm, tbl_nm, spark):
    df = hiveWH.executeQuery(f"select * from {db_nm}.{tbl_nm}")
    
    df.createOrReplaceTempView(tbl_nm)
    
    df = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                     + "' as table_name, 'unique count' as measure, 'primary key' as column_value, count(distinct " + prim_key
                                           + ") as freq from " + tbl_nm)
    df = df.toPandas()
    
    
    df2 = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                 + "' as table_name, 'record count' as measure, '' as column_value, count(*) as freq from " + tbl_nm)
    df2 = df2.toPandas()
    
    df3 = spark.sql("describe " + tbl_nm)
    df3 = df3.toPandas()
    

    df = df.append(df2)#, ignore_index = True)
    
    return df.append(pd.DataFrame([[db_nm, tbl_nm, 'field count', '', len(df3)]], columns=df.columns))

# 2. main function

def check_data_types(prim_key, db_nm, tbl_nm, spark):
    
    df = hiveWH.executeQuery(f"select * from {db_nm}.{tbl_nm}")
    
    df.createOrReplaceTempView(tbl_nm)
    
    df = spark.sql("describe " + tbl_nm)
    df = df.toPandas()
    
    df = df[(df.col_name != prim_key)]
    cat_df = df[df["data_type"].str.contains("varchar|string")] #Get only fields with categorical data types
    num_df = df[df["data_type"].str.contains("int|double|bigint|decimal")] #Get only fields with numeric data types
    date_df = df[df["data_type"].str.contains("date|timestamp")] #Get only fields with categorical data types

    # 2a. check categorical data types

    def check_string_types(db_nm, tbl_nm, cat_df):

        if len(cat_df) > 0:

            df_tmp = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "column_value", "freq"])
            df_cat = pd.DataFrame()

            for field in cat_df["col_name"]:
                
                df_tmp = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                             + "' as table_name, '" + field + "' as column_name, " + field
                                                         + " as column_value, count(*) as freq from " + tbl_nm
                                                         + " group by " + field)
                df_tmp = df_tmp.toPandas()
                
                if len(df_tmp) > 0:
                    df_cat = df_cat.append(df_tmp)
                else:
                    df_cat = df_cat.append(pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan]]))#,ignore_index = True))

        else:
            df_cat = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "column_value", "freq"])

        return df_cat


    # 2b. check numeric data types

    def check_numeric_types(db_nm, tbl_nm, num_df):

        if len(num_df) > 0:

            df_tmp = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "min", "max", "avg", "stddev", "10th_percentile", "20th_percentile", "30th_percentile", "40th_percentile", "50th_percentile", "60th_percentile", "70th_percentile", "80th_percentile", "90th_percentile", "null_values"])
            df_num = pd.DataFrame()

            for field in num_df["col_name"]:

                df_tmp = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                             + "' as table_name, '" + field + "' as column_name, min(" + field
                                                         + ") as min_value, max(" + field
                                                         + ") as max_value, avg(" + field
                                                         + ") as avg_value, stddev(" + field
                                                         + ") as stddev_value, percentile_approx(" + field
                                                         #+ ", 0.00) as 0th_percentile, percentile_approx(" + field
                                                         + ", 0.10) as 10th_percentile, percentile_approx(" + field
                                                         + ", 0.20) as 20th_percentile, percentile_approx(" + field
                                                         + ", 0.30) as 30th_percentile, percentile_approx(" + field
                                                         + ", 0.40) as 40th_percentile, percentile_approx(" + field
                                                         + ", 0.50) as 50th_percentile, percentile_approx(" + field
                                                         + ", 0.60) as 60th_percentile, percentile_approx(" + field
                                                         + ", 0.70) as 70th_percentile, percentile_approx(" + field
                                                         + ", 0.80) as 80th_percentile, percentile_approx(" + field
                                                         + ", 0.90) as 90th_percentile, sum(case when " + field
                                                         + " is null then 1 else 0 end) as null_values from " + tbl_nm)
                df_tmp = df_tmp.toPandas()
                
                if len(df_tmp) > 0:
                    df_num = df_num.append(df_tmp)
                else:
                    df_num = df_num.append(pd.DataFrame([[field, np.nan, np.nan, np.nan, np.nan, np.nan,
                    np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]]))#,ignore_index = True))

            df_num_unpivot = pd.melt(df_num, id_vars = ['schema_name', 'table_name', 'column_name'])

        else:
            #df_num_unpivot = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "column_value", "freq"])#made chngs 29/08
            df_num_unpivot = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "column_value", "variable","value"])
        return df_num_unpivot



    # 2c. check date data types

    def check_date_types(db_nm, tbl_nm, date_df):

        if len(date_df) > 0:

            df_tmp = pd.DataFrame(columns=["schema_name", "table_name", "column_name", 'date_type', "column_value", "freq"])
            df_date = pd.DataFrame()
            date_components = ["year", "month", "day"]
            measures = ["max", "min"]

            for field in date_df["col_name"]:
                for metric in date_components:

                    df_tmp = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                             + "' as table_name, '" + field + "' as column_name, '" + metric + "' as date_type, cast(" + metric + "(" + field
                                                             + ") as string)as column_value, count(*) as freq from " + tbl_nm
                                                             + " group by " + metric + "(" + field + ")")
                    df_tmp = df_tmp.toPandas()

                    if len(df_tmp) > 0:
                        df_date = df_date.append(df_tmp)
                    else:
                        df_date = df_date.append(pd.DataFrame([[field, np.nan, np.nan, np.nan, np.nan, np.nan]]))#,ignore_index = True))

            for field in date_df["col_name"]:
                for metric in measures:

                    df_tmp = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                             + "' as table_name, '" + field + "' as column_name, " + "'boundary' as date_type, '" + metric + "imum' as column_value, cast("
                                                            + metric + "(" + field + ") as string)as freq from " + tbl_nm)
                    df_tmp = df_tmp.toPandas()

                    if len(df_tmp) > 0:
                        df_date = df_date.append(df_tmp)
                    else:
                        df_date = df_date.append(pd.DataFrame([[field, np.nan, np.nan, np.nan, np.nan, np.nan]]))#,ignore_index = True))

        else:
            df_date = pd.DataFrame(columns=["schema_name", "table_name", "column_name", 'date_type', "column_value", "freq"])

        return df_date

    return check_string_types(db_nm, tbl_nm, cat_df), check_numeric_types(db_nm, tbl_nm, num_df), check_date_types(db_nm, tbl_nm, date_df)

# COMMAND ----------

import csv
db_nm_list=[]
tbl_list=[]
primary_key_list=[]
with open('AdvancedStats_Config.csv', newline='') as csvfile:
    rows = csv.reader(csvfile, delimiter=',')
    header=next(rows)
    for row in rows:
        if row[6]=='1':
            db_nm_list.append(row[1])
            tbl_list.append(row[2])
            primary_key_list.append(row[3])
            
            

# COMMAND ----------

# for db_nm,tbl,primary_key in zip(db_nm_list,tbl_list,primary_key_list):
#     #files prep
#     hive_primary_key_df = check_primary_key(primary_key, db_nm, tbl, spark)
#     dm_cat, dm_num, dm_date = check_data_types(primary_key, db_nm, tbl, spark)
#     hive_primary_key_df.to_csv(f'{export_path}Hive_{tbl}_metadata_count.csv',index=False,sep='|')
#     dm_cat.replace('','null').to_csv(f'{export_path}Hive_{tbl}_cat.csv',index=False,sep='|')
#     dm_num.replace('','null').to_csv(f'{export_path}Hive_{tbl}_num.csv',index=False,sep='|')
#     dm_date.replace('','null').to_csv(f'{export_path}Hive_{tbl}_date.csv',index=False,sep='|')
    

# COMMAND ----------

for db_nm,tbl,primary_key in zip(db_nm_list,tbl_list,primary_key_list):
    hive_primary_key_df = check_primary_key(primary_key, db_nm, tbl, spark)
    dm_cat, dm_num, dm_date = check_data_types(primary_key, db_nm, tbl, spark)
    hive_primary_key_df.replace('','null').to_csv('Hive_{}_metadata_count.csv'.format(tbl),index=False,sep='|')
    dm_cat.replace('','null').to_csv('Hive_{}_cat.csv'.format(tbl),index=False,sep='|')
    dm_num.replace('','null').to_csv('Hive_{}_num.csv'.format(tbl),index=False,sep='|')
    dm_date.replace('','null').to_csv('Hive_{}_date.csv'.format(tbl),index=False,sep='|')
