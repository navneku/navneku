# Databricks notebook source
# import libraries
import os
from pyspark.sql.window import Window
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as f
from pyspark.sql.functions import col, column, udf
from pyspark.sql.types import DoubleType
from pyspark.sql.types import StringType
from pyspark.sql.types import ArrayType
from pyspark.sql.types import IntegerType
from pyspark.sql.types import DateType
from pyspark.sql.types import FloatType
from datetime import datetime, timedelta
from pyspark.sql.window import *
from pyspark.sql.functions import row_number
from collections import Iterable
from pyspark.sql.functions import split, reverse
from pyspark.sql.functions import col, when
from pyspark.sql.functions import coalesce
from pyspark.sql.functions import regexp_replace
import datetime
from pyspark.sql.functions import lpad
from delta.tables import *
from pyspark.sql.functions import length
from pyspark.sql.functions import year, month, dayofmonth
from delta.tables import *
from datetime import date
import sys
from  pyspark.dbutils import FileInfo
from typing import List
import pandas as pd
import numpy as np
#from pyhive import hive
import requests
import json
import csv

# COMMAND ----------

spark.conf.set("spark.sql.execution.arrow.enabled", "true")# To optimise conversion of spark df to panda df
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")# To optimise conversion of spark df to panda df

# COMMAND ----------

#Hive settings
spark = SparkSession.builder.master('yarn')\
    .config('spark.app.name', 'Jugaad')\
    .config('spark.driver.memory', '5g')\
    .config('spark.executor.memory', '30g')\
    .config('spark.executor.instances', '1')\
    .config('spark.executor.cores', '5')\
    .config('spark.submit.deployMode', 'client')\
    .config('spark.jars', '/usr/hdp/current/hive_warehouse_connector/hive-warehouse-connector-assembly-1.0.0.3.1.4.100-4.jar')\
    .config('spark.submit.pyFiles', '/usr/hdp/current/hive_warehouse_connector/pyspark_hwc-1.0.0.3.1.4.100-4.zip')\
    .config('spark.security.credentials.hiveserver2.enabled', 'false')\
    .config('spark.port.maxRetries', '50')\
    .config('spark.yarn.queue', 'analytics')\
    .enableHiveSupport().getOrCreate()

#from pyspark_llap.sql.session import HiveWarehouseSession
#hiveWH = HiveWarehouseSession.session(spark).build()

# COMMAND ----------

server_name = "jdbc:sqlserver://mfcsynap-sea-ngedl-nonprod-02.sql.azuresynapse.net:1433;database=ngenedlkhsqlpool02;user=sqladminuser@mfcsynap-sea-ngedl-nonprod-02;password={your_password_here};encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.sql.azuresynapse.net;loginTimeout=30;"
database_name = "ngenedlkhsqlpool02"
url = server_name + "," + "databaseName=" + database_name + ";"

#table_name ="curated.cip_kh_polclm_owndp"
username ="sqladminuser"
password="P@ssw0rd"

# COMMAND ----------

#ADLS Gen 2 Connection details
wandisco_container = "abfss://wandisco@abcmfcadoedl01psea.dfs.core.windows.net/"
test_container = "abfss://dev@abcmfcadoedl01psea.dfs.core.windows.net/"
wandisco_container_name = "wandisco"
storage_account = "abcmfcadoedl01dsea"
storage_secret = "SfK1BIilvd1ghEQ8eSvtXpqw8ZYG30q2uhEVtKFfw/g+DXZqiZzqC6d5Kih6kuP40GmQXKt3RJhE73LQ3AKdHA=="
dbfs_mount_path ='/mnt/'
wandisco_test_result_metrics_folder ='Wandisco_Metrics'
test_container_name ='dev'

#test script config files
MetadataConfig = 'Metadata_Config.csv'
AdvancedStatsConfig = 'AdvancedStats_Config.csv'
OracleAdvancedStatsConfig = 'Oracle_AdvancedStats_Config.csv'

# COMMAND ----------

#File type format
ORC_FORMAT ="orc"
CSV_FORMAT="csv"
PARQUET_FORMAT ="parquet"
AVRO_FORMAT = "avro"

# COMMAND ----------

#Oracle Connection details
oracle_url = "jdbc:oracle:thin:@10.216.133.11:1521/KHCASREG"
oracle_username = "edl"
oracle_password = "edlreg"
