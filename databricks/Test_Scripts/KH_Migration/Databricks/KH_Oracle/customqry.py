# Databricks notebook source
# MAGIC %run ../02_Utilities

# COMMAND ----------

# DBTITLE 1,Inputv (testing use)
# inputv = [{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":10,"SrcObject":"TFRANCHISE_ADDRESSES","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"HH","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20},{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":600393,"SrcObject":"TLOAN_DETAILS","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"DD","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20}]
#{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":84,"SrcObject":"TWRK_VALUATION_EXTRACT","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"HH","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20}]
#[{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":62,"SrcObject":"TCASH_BATCH_DETAILS","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"HH","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20},

# COMMAND ----------

# inputv is the params from ADF which is from FwkConfig table 
#inputv = dbutils.widgets.get('FwkConfig_value')
varFwkTriggerId=1001
varFwkSourceId=13
varDatabaseName='TestKHCASREG'
varSchemaName='TestSchema'
varSrcPath='NULL'
varSrcObject='table'
varTypeLoad=1
varWmkColumnName=1
varWmkDataType=1
varSinkPathGranularity='DD'
varConvertMethodvarBatchGroupId='Databricks'
varSynapseObject='Null'
varActiveFlag='Y'
varRelativeURL='null'
varHeader01='null'
varHeader02='null'
varEnvironmentName='dev'
varCountryId='KH'
varSystemName='AWS'
varMaxConcurrency=50
varBlockSizevarMaxRowPerFile=100
VarMaxRowPerFile='null'
varDegreeOfParallelism=50
varLastUpdate=''
varCreatedBy='Elango'
insert into [dbo].[FwkConfig](FwkTriggerId,FwkSourceId,DatabaseName,SchemaName,SrcPath,SrcObject,TypeLoad,WmkColumnName,WmkDataType,SinkPathGranularity,ConvertMethod,BatchGroupId,SynapseObject,ActiveFlag,RelativeURL,Header01,Header02,EnvironmentName,CountryId,SystemName,MaxConcurrency,BlockSize,MaxRowPerFile,DegreeOfParallelism,LastUpdate,CreatedBy) values ()

#inputv = [{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":10,"SrcObject":"TFRANCHISE_ADDRESSES","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"HH","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20},{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":600393,"SrcObject":"TLOAN_DETAILS","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"DD","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20}]
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
row_cnt_qry="select count(*) from tablevar"
column_cnt_query="select * from tablevar limit 1"
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
    #rowcount =df.count()
    #columncount=len(df.columns)
    df.createOrReplaceTempView("tablevar")
    df3=spark.sql(column_cnt_query)
    columncount=len(df3.columns)
    df4=spark.sql(row_cnt_qry)
    rowcount=df4.head()[0]
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

# inputv is the params from ADF which is from FwkConfig table 
#inputv = dbutils.widgets.get('FwkConfig_value')
varTriggerid='10001'
FwkSourceId,DatabaseName,SchemaName,SrcPath,SrcObject,TypeLoad,WmkColumnName,WmkDataType,SinkPathGranularity,ConvertMethod,BatchGroupId,SynapseObject,ActiveFlag,RelativeURL,Header01,Header02,EnvironmentName,CountryId,SystemName,MaxConcurrency,BlockSize,MaxRowPerFile,DegreeOfParallelism,LastUpdate,CreatedBy
insertQry='insert into [dbo].[FwkConfig](FwkTriggerId,FwkSourceId,DatabaseName,SchemaName,SrcPath,SrcObject,TypeLoad,WmkColumnName,WmkDataType,SinkPathGranularity,ConvertMethod,BatchGroupId,SynapseObject,ActiveFlag,RelativeURL,Header01,Header02,EnvironmentName,CountryId,SystemName,MaxConcurrency,BlockSize,MaxRowPerFile,DegreeOfParallelism,LastUpdate,CreatedBy) values (varFwkTriggerId,varFwkSourceId,varDatabaseName,varSchemaName,varSrcPath,varSrcObject,varTypeLoad,varWmkColumnName,varWmkDataType,varSinkPathGranularity,varConvertMethod,varBatchGroupId,varSynapseObject,varActiveFlag,varRelativeURL,varHeader01,varHeader02,varEnvironmentName,varCountryId,varSystemName,varMaxConcurrency,varBlockSize,varMaxRowPerFile,varDegreeOfParallelism,varLastUpdate,varCreatedBy
)'


#inputv = [{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":10,"SrcObject":"TFRANCHISE_ADDRESSES","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"HH","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20},{"FwkSourceId":13,"SourceType":"Oracle","FwkConfigId":600393,"SrcObject":"TLOAN_DETAILS","SchemaName":"CAS","DatabaseName":"KHCASREG","WmkColumnName":"1","WmkDataType":1,"TypeLoad":1,"RelativeURL":"null","ActiveFlag":"Y","Header01":"null","Header02":"null","InstanceURL":"null","Port":"null","UserName":"null","SecretName":"null","SrcPath":"null","SinkPathGranularity":"DD","IPAddress":"null","FwkTriggerId":24,"BatchGroupId":-1,"ConvertMethod":"Databricks","SynapseObject":"null","EnvironmentName":"dev","CountryId":"KH","SystemName":"Oracle","TimezoneName":"SE Asia Standard Time","MaxConcurrency":50,"BlockSize":100,"DegreeOfParallelism":20}]
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
row_cnt_qry="select count(*) from tablevar"
column_cnt_query="select * from tablevar limit 1"
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
    #rowcount =df.count()
    #columncount=len(df.columns)
    df.createOrReplaceTempView("tablevar")
    df3=spark.sql(column_cnt_query)
    columncount=len(df3.columns)
    df4=spark.sql(row_cnt_qry)
    rowcount=df4.head()[0]
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
    file_path = f'/Published/KH/Master/KH_PUBLISHED_CAS_DB/{tbl}'
    #print(tblnm)
    df = load_adls_df(file_path,file_format)
    rowcount =df.count()
    columncount=len(df.columns)
    df = df.select(f.lit(tblnm).alias("tblnm"),f.lit(columncount).alias("columncount"),f.lit(rowcount).alias("rowcount")).distinct()
    df_final_adls = df_final_adls.union(df)

display(df_final_adls)

# COMMAND ----------

from pyspark.sql.functions import *
#Comparison
df_final_oracle = df_final_oracle.withColumn('tblnm_oracle',f.expr("substring_index(tblnm_oracle,'.',-1)"))
result_df = df_final_adls.join(df_final_oracle,df_final_adls.tblnm==df_final_oracle.tblnm_oracle,"left")
result_df = result_df.withColumn('ComparisonResult',\
f.when((f.col("rowcount")==f.col("rowcount_oracle")) & (f.col("columncount")-2==f.col("columncount_oracle")),"Both matched")\
.when((f.col("rowcount")!=f.col("rowcount_oracle")) & (f.col("columncount")-2==f.col("columncount_oracle")),"Row count not match")\
.when((f.col("rowcount")==f.col("rowcount_oracle")) & (f.col("columncount")-2!=f.col("columncount_oracle")),"Column count not match")\
.otherwise("Both not match"))\
.withColumn("current_timestamp",current_timestamp())

display(result_df)


#columncount from adls will be greater than columncount_oralce for 2 since the LastUpdate & Createdby column will generated on the fly therefore -2 for columncount is added to the code

# COMMAND ----------


