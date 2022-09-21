# Databricks notebook source
# MAGIC %run ../02_Utilities

# COMMAND ----------

# DBTITLE 1,Inputv (testing use)
# inputv = [{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":10,"SrcObject":"TFRANCHISE_ADDRESSES","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"HH","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20},{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":600393,"SrcObject":"TLOAN_DETAILS","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"DD","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20}]
#{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":84,"SrcObject":"TWRK_VALUATION_EXTRACT","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"HH","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20}]
#[{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":62,"SrcObject":"TCASH_BATCH_DETAILS","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"HH","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20},

# COMMAND ----------

# inputv is the params from ADF which is from FwkConfig table 
inputv = dbutils.widgets.get('FwkConfig_value')

rdd =  spark.sparkContext.parallelize([inputv])
input_df = spark.read.json(rdd)
input_df_oralce = input_df.filter(input_df.SourceType == 'Oracle')
tbl_schema_list = input_df_oralce.select('SchemaName').rdd.flatMap(lambda x:x).collect()
tbl_name_list = input_df_oralce.select('SrcObject').rdd.flatMap(lambda x:x).collect()
print(tbl_schema_list)
print(tbl_name_list)

#Read Oralce data
ddlSchema = StructType([
StructField('tblnm',StringType()),
StructField('columncount',StringType()),
StructField('rowcount',IntegerType())])
df_final_oracle = spark.createDataFrame([],ddlSchema)
for tb_sch_nm,tbl in zip(tbl_schema_list,tbl_name_list):
    qry = f'select * from {tb_sch_nm}.{tbl}'
    tblnm = tbl
    df = spark.read \
    .format("jdbc") \
    .option("url", oracle_url) \
    .option("query",qry)\
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

#print(inputv)

# COMMAND ----------

#Read ADLSgen2 data
container = 'dev'
file_format = PARQUET_FORMAT
mount_container(container)
mnt_path = dbfs_mount_path+container

df_final_adls = spark.createDataFrame([],ddlSchema)
for tbl in tbl_name_list:
    tblnm= tbl
    file_path = f'/Published/KH/Master/Oracle/{tbl}'
    #print(tblnm)
    df = load_adls_df(file_path,file_format)
    rowcount =df.count()
    columncount=len(df.columns)
    df = df.select(f.lit(tblnm).alias("tblnm"),f.lit(columncount).alias("columncount"),f.lit(rowcount).alias("rowcount")).distinct()
    df_final_adls = df_final_adls.union(df)

display(df_final_adls)

# COMMAND ----------

#Comparison
df_final_oracle = df_final_oracle.withColumn('tblnm_oracle',f.expr("substring_index(tblnm_oracle,'.',-1)"))
result_df = df_final_adls.join(df_final_oracle,df_final_adls.tblnm==df_final_oracle.tblnm_oracle,"left")
result_df = result_df.withColumn('ComparisonResult',\
f.when((f.col("rowcount")==f.col("rowcount_oracle")) & (f.col("columncount")-2==f.col("columncount_oracle")),"Both matched")\
.when((f.col("rowcount")!=f.col("rowcount_oracle")) & (f.col("columncount")-2==f.col("columncount_oracle")),"Row count not match")\
.when((f.col("rowcount")==f.col("rowcount_oracle")) & (f.col("columncount")-2!=f.col("columncount_oracle")),"Column count not match")\
.otherwise("Both not match"))
display(result_df)


#columncount from adls will be greater than columncount_oralce for 2 since the LastUpdate & Createdby column will generated on the fly therefore -2 for columncount is added to the code

# COMMAND ----------

# DBTITLE 1,Pass the parameters value here:
# container = 'dev'
# file_format = 'parquet'
# mount_container(container)
# mnt_path = dbfs_mount_path+container
# #add all the tbl name with schema here (comma separated values)
# tbl_list =['CAS.TAIS_UW_DATA',
#                 'CAS.TCASH_BATCH_DETAILS',
#                 'CAS.TCLAIM_DETAILS',
#                 'CAS.TCLIENT_DETAILS',
#                 'CAS.TCLIENT_OTHER_DETAILS',
#                 'CAS.TCLIENT_POLICY_LINKS',
#                 'CAS.TCOVERAGES',
#                 'CAS.TFIELD_VALUES',
#                 'CAS.TFRANCHISE_ADDRESSES',
#                 'CAS.TKH_POLICY_HIS',
#                 'CAS.TOCCUPATION',
#                 'CAS.TORPHAN_POLICIES',
#                 'CAS.TPLANS',
#                 'CAS.TPOLICYS',
#                 'CAS.TPOLICYS_INFO',
#                 'CAS.TTRXN_HISTORIES',
#                 'CAS.TWRK_VALUATION_EXTRACT',
#                 'CAS.TCLIENT_ADDRESSES',
#                 'CAS.TCONTROL_PARAMETERS',
#                 'CAS.TLOAN_DETAILS',
#                 'CAS.TPRODUCTS']


# #add all the tbl paths here (comma separated values)
# File_path_list =['/Published/KH/Master/Oracle/TAIS_UW_DATA',
#                  '/Published/KH/Master/Oracle/TCASH_BATCH_DETAILS',
#                 '/Published/KH/Master/Oracle/TCLAIM_DETAILS',
#                 '/Published/KH/Master/Oracle/TCLIENT_DETAILS',
#                 '/Published/KH/Master/Oracle/TCLIENT_OTHER_DETAILS',
#                 '/Published/KH/Master/Oracle/TCLIENT_POLICY_LINKS',
#                 '/Published/KH/Master/Oracle/TCOVERAGES',
#                 '/Published/KH/Master/Oracle/TFIELD_VALUES',
#                 '/Published/KH/Master/Oracle/TFRANCHISE_ADDRESSES',
#                 '/Published/KH/Master/Oracle/TKH_POLICY_HIS',
#                 '/Published/KH/Master/Oracle/TOCCUPATION',
#                 '/Published/KH/Master/Oracle/TORPHAN_POLICIES',
#                 '/Published/KH/Master/Oracle/TPLANS',
#                 '/Published/KH/Master/Oracle/TPOLICYS',
#                 '/Published/KH/Master/Oracle/TPOLICYS_INFO',
#                 '/Published/KH/Master/Oracle/TTRXN_HISTORIES',
#                 '/Published/KH/Master/Oracle/TWRK_VALUATION_EXTRACT',
#                 '/Published/KH/Master/Oracle/TCLIENT_ADDRESSES',
#                 '/Published/KH/Master/Oracle/TCONTROL_PARAMETERS',
#                 '/Published/KH/Master/Oracle/TLOAN_DETAILS',
#                 '/Published/KH/Master/Oracle/TPRODUCTS']

# COMMAND ----------

# ddlSchema = StructType([
# StructField('tblnm',StringType()),
# StructField('columncount',StringType()),
# StructField('rowcount',IntegerType())])
# df_final_oracle = spark.createDataFrame([],ddlSchema)
# for tbl in tbl_list:
#     #tblnm= file_path.split('/')[-1]
#     tblnm = tbl
#     df = spark.read \
#     .format("jdbc") \
#     .option("url", oracle_url) \
#     .option("dbtable", tbl) \
#     .option("user", oracle_username) \
#     .option("password", oracle_password) \
#     .option("driver", "oracle.jdbc.driver.OracleDriver") \
#     .load()
#     rowcount =df.count()
#     columncount=len(df.columns)
#     df = df.select(f.lit(tblnm).alias("tblnm"),f.lit(columncount).alias("columncount"),f.lit(rowcount).alias("rowcount")).distinct()
#     df_final_oracle = df_final_oracle.union(df)

    
# df_final_oracle = (
# df_final_oracle
#     .withColumnRenamed("tblnm","tblnm_oracle")
#     .withColumnRenamed("columncount","columncount_oracle")
#     .withColumnRenamed("rowcount","rowcount_oracle")
# )
# display(df_final_oracle)



# COMMAND ----------

# df_final_adls = spark.createDataFrame([],ddlSchema)
# for file_path in File_path_list:
#     tblnm= file_path.split('/')[-1]
#     #print(tblnm)
#     df = load_adls_df(file_path,file_format)
#     rowcount =df.count()
#     columncount=len(df.columns)
#     df = df.select(f.lit(tblnm).alias("tblnm"),f.lit(columncount).alias("columncount"),f.lit(rowcount).alias("rowcount")).distinct()
#     df_final_adls = df_final_adls.union(df)

# display(df_final_adls)

# COMMAND ----------

# df_final_oracle = df_final_oracle.withColumn('tblnm_oracle',f.expr("substring_index(tblnm_oracle,'.',-1)"))
# result_df = df_final_adls.join(df_final_oracle,df_final_adls.tblnm==df_final_oracle.tblnm_oracle,"left")
# result_df = result_df.withColumn('ComparisonResult',\
# f.when((f.col("rowcount")==f.col("rowcount_oracle")) & (f.col("columncount")-2==f.col("columncount_oracle")),"Both matched")\
# .when((f.col("rowcount")!=f.col("rowcount_oracle")) & (f.col("columncount")-2==f.col("columncount_oracle")),"Row count not match")\
# .when((f.col("rowcount")==f.col("rowcount_oracle")) & (f.col("columncount")-2!=f.col("columncount_oracle")),"Column count not match")\
# .otherwise("Both not match"))
# display(result_df)

# #columncount from adls will be greater than columncount_oralce for 2 since the LastUpdate & Createdby column will generated on the fly therefore -2 for columncount is added to the code
