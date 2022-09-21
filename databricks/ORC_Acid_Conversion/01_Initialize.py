# Databricks notebook source
# import libraries
import os
from pyspark.sql.window import Window
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import *
import pyspark.sql.functions as f
from pyspark.sql.functions import col, column, udf
from pyspark.sql.types import StructType,StructField
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
from pyhive import hive
import requests
import json
import csv

# COMMAND ----------

#spark config properties
spark.conf.set("spark.sql.execution.arrow.enabled", "true")# To optimise conversion of spark df to panda df
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")# To optimise conversion of spark df to panda df
spark.conf.set("spark.sql.broadcastTimeout","-1") #adding it to fix 300sec default timeout execution
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1") #adding to fix out of memory exception due to broadcast table limit
spark.conf.set("spark.sql.files.ignoreCorruptFiles","true")# To ignore metadata_Acid/any footer/corrupted files in the paths
spark.conf.set("spark.databricks.adaptive.autoOptimizeShuffle.enabled", "true")# To optimise partition 

# COMMAND ----------

#ADLS Gen 2 Connection details
wandisco_container = "abfss://wandisco@abcmfcadoedl01psea.dfs.core.windows.net/"
test_container = "abfss://prod@abcmfcadoedl01psea.dfs.core.windows.net/"
wandisco_container_name = "wandisco"
storage_account = "abcmfcadoedl01dsea"
storage_secret = "SfK1BIilvd1ghEQ8eSvtXpqw8ZYG30q2uhEVtKFfw/g+DXZqiZzqC6d5Kih6kuP40GmQXKt3RJhE73LQ3AKdHA=="
dbfs_mount_path ='/mnt/'
wandisco_test_result_metrics_folder ='Wandisco_Metrics'
test_container_name ='dev'

#test script config files
MetadataConfig = 'Metadata_Config.csv'
AdvancedStatsConfig = 'AdvancedStats_Config.csv'

# COMMAND ----------

#File type format
ORC_FORMAT ="ORC"
CSV_FORMAT="CSV"
PARQUET_FORMAT ="PARQUET"
AVRO_FORMAT = "AVRO"
