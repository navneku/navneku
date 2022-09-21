# Databricks notebook source
# MAGIC %run ../02_Utilities

# COMMAND ----------

# DBTITLE 1,Pass the parameters value here:
tbl_list =['CAS.ACT_SCH',
'CAS.CONV_HCP',
'CAS.CONV_HOSPITAL',
'CAS.CONV_MCLM',
'CAS.CONV_PROLADY',
'CAS.DIRECTORIES',
'CAS.FRM45_ENABLED_ROLES',
'CAS.HC_TDATES_CONTROL',
'CAS.MVCAS_AGT_RPT_RELS',
'CAS.MVCAS_AGT_RPT_RELS_BK',
'CAS.NSP_PUA',
'CAS.POL_CTL',
'CAS.QUEST_SL_TEMP_EXPLAIN1',
'CAS.TACCT_EXTRACTS',
'CAS.TACCT_EXTRACTS_HISTORIES',
'CAS.TACCT_EXTRACTS_NP',
'CAS.TACCT_MAP',
'CAS.TACCT_PAR_FEED',
'CAS.TACCT_RATES_NP',
'CAS.TACTIVITY_LOGS',
'CAS.TACTIVITY_SCHEDULES',
'CAS.TADDR_ANALYSIS',
'CAS.TADD_CLIENT_INFO',
'CAS.TADD_CLIENT_INFO_SH',
'CAS.TADD_CLIENT_LABELS',
'CAS.TAGENTS_WK',
'CAS.TAGENTS_WK_SH',
'CAS.TAGENT_ADJUST',
'CAS.TAGENT_BLACK_LIST',
'CAS.TAGENT_CASH_SLIP_DETAILS',
'CAS.TAGENT_CASH_SLIP_DETAILS_BK',
'CAS.TAGENT_CONNECTION',
'CAS.TAGENT_NOTICES',
'CAS.TAGENT_PROFILES_SH',
'CAS.TAIS_ADMIN_ANS_DET',
'CAS.TAIS_ADMIN_RULE_MAST',
'CAS.TAIS_ALPHA_SEARCH_ID',
'CAS.TAIS_BASE_QTNS',
'CAS.TAIS_CAS_MAPPING_CTRL',
'CAS.TAIS_CLI_MAPPING',
'CAS.TAIS_FILTER',
'CAS.TAIS_FLTR_VALUS',
'CAS.TAIS_IF02_XML',
'CAS.TAIS_LOG',
'CAS.TAIS_OFFLINE_XML',
'CAS.TAIS_PARAMETER_CTRL',
'CAS.TAIS_PARAMETER_RISK_SETUP',
'CAS.TAIS_PARAMETER_SRC',
'CAS.TAIS_PARAM_RULE_MAP',
'CAS.TAIS_POL_PARAMETER']

container = 'dev'
file_format = 'parquet'
#add all the tbl paths here (comma separated values)
File_path_list =['/Published/KH/Master/CAS/ACT_SCH/',
'/Published/KH/Master/CAS/CONV_HCP/',
'/Published/KH/Master/CAS/CONV_HOSPITAL/',
'/Published/KH/Master/CAS/CONV_MCLM/',
'/Published/KH/Master/CAS/CONV_PROLADY/',
'/Published/KH/Master/CAS/DIRECTORIES/',
'/Published/KH/Master/CAS/FRM45_ENABLED_ROLES/',
'/Published/KH/Master/CAS/HC_TDATES_CONTROL/',
'/Published/KH/Master/CAS/MVCAS_AGT_RPT_RELS/',
'/Published/KH/Master/CAS/MVCAS_AGT_RPT_RELS_BK/',
'/Published/KH/Master/CAS/NSP_PUA/',
'/Published/KH/Master/CAS/POL_CTL/',
'/Published/KH/Master/CAS/QUEST_SL_TEMP_EXPLAIN1/',
'/Published/KH/Master/CAS/TACCT_EXTRACTS/',
'/Published/KH/Master/CAS/TACCT_EXTRACTS_HISTORIES/',
'/Published/KH/Master/CAS/TACCT_EXTRACTS_NP/',
'/Published/KH/Master/CAS/TACCT_MAP/',
'/Published/KH/Master/CAS/TACCT_PAR_FEED/',
'/Published/KH/Master/CAS/TACCT_RATES_NP/',
'/Published/KH/Master/CAS/TACTIVITY_LOGS/',
'/Published/KH/Master/CAS/TACTIVITY_SCHEDULES/',
'/Published/KH/Master/CAS/TADDR_ANALYSIS/',
'/Published/KH/Master/CAS/TADD_CLIENT_INFO/',
'/Published/KH/Master/CAS/TADD_CLIENT_INFO_SH/',
'/Published/KH/Master/CAS/TADD_CLIENT_LABELS/',
'/Published/KH/Master/CAS/TAGENTS_WK/',
'/Published/KH/Master/CAS/TAGENTS_WK_SH/',
'/Published/KH/Master/CAS/TAGENT_ADJUST/',
'/Published/KH/Master/CAS/TAGENT_BLACK_LIST/',
'/Published/KH/Master/CAS/TAGENT_CASH_SLIP_DETAILS/',
'/Published/KH/Master/CAS/TAGENT_CASH_SLIP_DETAILS_BK/',
'/Published/KH/Master/CAS/TAGENT_CONNECTION/',
'/Published/KH/Master/CAS/TAGENT_NOTICES/',
'/Published/KH/Master/CAS/TAGENT_PROFILES_SH/',
'/Published/KH/Master/CAS/TAIS_ADMIN_ANS_DET/',
'/Published/KH/Master/CAS/TAIS_ADMIN_RULE_MAST/',
'/Published/KH/Master/CAS/TAIS_ALPHA_SEARCH_ID/',
'/Published/KH/Master/CAS/TAIS_BASE_QTNS/',
'/Published/KH/Master/CAS/TAIS_CAS_MAPPING_CTRL/',
'/Published/KH/Master/CAS/TAIS_CLI_MAPPING/',
'/Published/KH/Master/CAS/TAIS_FILTER/',
'/Published/KH/Master/CAS/TAIS_FLTR_VALUS/',
#'/Published/KH/Master/CAS/TAIS_IF02_XML/',
'/Published/KH/Master/CAS/TAIS_LOG/',
'/Published/KH/Master/CAS/TAIS_OFFLINE_XML/',
'/Published/KH/Master/CAS/TAIS_PARAMETER_CTRL/',
'/Published/KH/Master/CAS/TAIS_PARAMETER_RISK_SETUP/',
'/Published/KH/Master/CAS/TAIS_PARAMETER_SRC/',
'/Published/KH/Master/CAS/TAIS_PARAM_RULE_MAP/',
'/Published/KH/Master/CAS/TAIS_POL_PARAMETER/']

mount_container(container)
mnt_path = dbfs_mount_path+container

# COMMAND ----------

ddlSchema = StructType([
StructField('tblnm',StringType()),
StructField('columncount',StringType()),
StructField('rowcount',IntegerType())])
df_final_oracle = spark.createDataFrame([],ddlSchema)
for tbl in tbl_list:
    #tblnm= file_path.split('/')[-1]
    tblnm = tbl
    df = spark.read \
    .format("jdbc") \
    .option("url", oracle_url) \
    .option("dbtable", tbl) \
    .option("user", oracle_username) \
    .option("password", oracle_password) \
    .option("driver", "oracle.jdbc.driver.OracleDriver") \
    .load()
    rowcount =df.count()
    columncount=len(df.columns)
    df = df.select(f.lit(tblnm).alias("tblnm"),f.lit(columncount).alias("columncount"),f.lit(rowcount).alias("rowcount")).distinct()
    df_final_oracle = df_final_oracle.union(df)

    
df_final_oracle = (
df_final_oracle
    .withColumnRenamed("tblnm","tblnm_oracle")
    .withColumnRenamed("columncount","columncount_oracle")
    .withColumnRenamed("rowcount","rowcount_oracle")
)
display(df_final_oracle)



# COMMAND ----------

# Table count
tblcount=0
master_path ='/Published/KH/Master/CAS/'
path_list = dbutils.fs.ls(mnt_path+master_path)
py_tbl_list =[]
if path_list:
    #print(path_list)
    for path_object in path_list:
        #print(path_object.path)
        if path_object.path.replace("dbfs:/mnt/dev","") in File_path_list:
            tblcount += 1
            py_tbl_list.append(path_object.path.replace("dbfs:"+dbfs_mount_path+container,""))
            
#print(tblcount)
df_final_adls = row_column_count(py_tbl_list)
display(df_final_adls)

# COMMAND ----------

df_final_oracle = df_final_oracle.withColumn('tblnm_oracle',f.expr("substring_index(tblnm_oracle,'.',-1)"))
result_df = df_final_adls.join(df_final_oracle,df_final_adls.tblnm==df_final_oracle.tblnm_oracle,"left")
result_df = result_df.withColumn('ComparisonResult',\
f.when((f.col("rowcount")==f.col("rowcount_oracle")) & (f.col("columncount")-2==f.col("columncount_oracle")),"Both matched")\
.when((f.col("rowcount")!=f.col("rowcount_oracle")) & (f.col("columncount")-2==f.col("columncount_oracle")),"Row count not match")\
.when((f.col("rowcount")==f.col("rowcount_oracle")) & (f.col("columncount")-2!=f.col("columncount_oracle")),"Column count not match")\
.otherwise("Both not match"))
display(result_df)

#columncount from adls will be greater than columncount_oralce for 2 since the LastUpdate & Createdby column will generated on the fly therefore -2 for columncount is added to the code
