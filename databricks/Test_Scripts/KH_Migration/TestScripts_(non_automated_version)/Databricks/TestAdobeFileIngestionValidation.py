# Databricks notebook source
# MAGIC %run ./02_Utilities

# COMMAND ----------

container = 'dev'
file_format = 'parquet'
master_path ='/Published/KH/Master/kh_published_adobe_allsites_db/'

# COMMAND ----------

#add all the tbl paths here (comma separated values)
File_path_list =['/Published/KH/Master/kh_published_adobe_allsites_db/BROWSER/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/BROWSER_TYPE/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/COLOR_DEPTH/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/COLUMN_HEADERS/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/CONNECTION_TYPE/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/COUNTRY/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/EVENT/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/JAVASCRIPT_VERSION/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/LANGUAGES/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/PLUGINS/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/REFERRER_TYPE/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/RESOLUTION/',
                 '/Published/KH/Master/kh_published_adobe_allsites_db/HIT_DATA/2022/09/19/',
                 '/Published/KH/Master/kh_published_adobe_allsites_db/OPERATING_SYSTEMS/',
                '/Published/KH/Master/kh_published_adobe_allsites_db/SEARCH_ENGINES/']
mount_container(container)
mnt_path = dbfs_mount_path+container
#print(mnt_path+master_path)
dbutils.fs.ls(mnt_path+master_path)


# COMMAND ----------

#Row count & Column count
ddlSchema = StructType([
StructField('tblnm',StringType()),
StructField('columncount',StringType()),
StructField('rowcount',IntegerType())])
df_final_adls = spark.createDataFrame([],ddlSchema)
for file_path in File_path_list:
    tblnm= file_path.split('/')[-2].lower()
   # print(tblnm.lower())
    print(file_path)
    df = load_adls_df(file_path,file_format)
    #display(df)
    rowcount =df.count()
    columncount=len(df.columns)
    df = df.select(f.lit(tblnm).alias("tblnm"),f.lit(columncount).alias("columncount"),f.lit(rowcount).alias("rowcount")).distinct()
    df_final_adls = df_final_adls.union(df)
display(df_final_adls)


# COMMAND ----------

container = 'dev'
file_format = 'tsv'
master_path ='/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip'
#add all the tbl paths here (comma separated values)
File_Name_List =['/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/browser.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/browser_type.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/color_depth.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/column_headers.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/connection_type.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/country.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/event.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/javascript_version.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/languages.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/plugins.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/referrer_type.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/resolution.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/hit_data.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/operating_systems.tsv',
                '/Staging/Loading/manufin-manulifecomph-prod_2021-07-23.zip/search_engines.tsv']
mount_container(container)
mnt_path = dbfs_mount_path+container
#print(mnt_path+master_path)
#dbutils.fs.ls(mnt_path+master_path)

# COMMAND ----------

#Row count & Column count
ddlSchema = StructType([
StructField('tblnm',StringType()),
StructField('columncount',StringType()),
StructField('rowcount',IntegerType())])
df_final_org = spark.createDataFrame([],ddlSchema)
for file_path in File_Name_List:
    tblnm= file_path.split('/')[-1].split('.')[0].lower()
    print(tblnm.lower())
    print(file_path)
    df = load_adls_df(file_path,file_format)
    #display(df)
    rowcount =df.count()
    columncount=len(df.columns)
    df = df.select(f.lit(tblnm).alias("tblnm"),f.lit(columncount).alias("columncount"),f.lit(rowcount).alias("rowcount")).distinct()
    df_final_org = df_final_org.union(df)
display(df_final_org)


# COMMAND ----------

df_final_org = (
df_final_org
    .withColumnRenamed("tblnm","tblnm_ftp")
    .withColumnRenamed("columncount","columncount_ftp")
    .withColumnRenamed("rowcount","rowcount_ftp")
)

# COMMAND ----------

result_df = df_final_adls.join(df_final_org,df_final_adls.tblnm==df_final_org.tblnm_ftp,"right")
result_df = result_df.withColumn('ComparisonResult',\
f.when((f.col("rowcount")==f.col("rowcount_ftp")) & (f.col("columncount")-2==f.col("columncount_ftp")),"Both matched")\
.when((f.col("rowcount")!=f.col("rowcount_ftp")) & (f.col("columncount")-2==f.col("columncount_ftp")),"Row count not match")\
.when((f.col("rowcount")==f.col("rowcount_ftp")) & (f.col("columncount")-2!=f.col("columncount_ftp")),"Column count not match")\
.otherwise("Both not match"))
display(result_df)

# COMMAND ----------


