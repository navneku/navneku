# Databricks notebook source
# DBTITLE 1,How To  Run This Notebook
# MAGIC %md
# MAGIC This notebook will create advanced metrics for table file in ADLS and compare it with hive mertics
# MAGIC * This Notebook is invoked by 3.2_Advanced_Statistics_Main.
# MAGIC * This notebook can also  run individually if you need Advanced stats metrics for Table.
# MAGIC 
# MAGIC * Prerequisties:
# MAGIC   * Hive metrics must be generated(using jupyter hub/Putty notebook)
# MAGIC   
# MAGIC * To run this notebook individually for getting Advanced stats for one particular table, follow the below steps:
# MAGIC   * Run cmd 3, widgets will appear on the top with below tags, fill them, below are the samples:
# MAGIC      * ContainerName : wandisco
# MAGIC      * DBSchema : kh_dev_published_src_cas_db
# MAGIC      * FileFormat : orc (generally  it will be orc, parquet, csv  else give 'orc-acid' if its table file with transactional property enabled)
# MAGIC      * FilePath : /kh/dev/published/hive/kh_dev_published_src_cas_db/plan_needs_mapping/delta_0000001_0000001_0000 (#give the path where final file is present )
# MAGIC      * PrimaryKey : plan_cd (# primary key for that table)
# MAGIC      * TableName : plan_needs_mapping (name of the table)
# MAGIC   * Pass the values in the above widgets, run cmd 3 again.
# MAGIC   * Run upto cmd 4 & upload the hive metrics file in the file location created by running command 4 (wandisco/Test_Validation/Advanced_Statistics/yyyMMdd/)
# MAGIC   * Once the above two are done run the entire notebook 

# COMMAND ----------

# MAGIC %run ./02_Utilities

# COMMAND ----------

# DBTITLE 1,Pass the parameters value here:
dbutils.widgets.removeAll()
dbutils.widgets.text("DBSchema","")
dbutils.widgets.text("TableName","")
dbutils.widgets.text("PrimaryKey","")
dbutils.widgets.text("ContainerName","")
dbutils.widgets.text("FilePath","")
dbutils.widgets.text("FileFormat","")

DBSchema = dbutils.widgets.get("DBSchema")
TableName = dbutils.widgets.get("TableName")
PrimaryKey = dbutils.widgets.get("PrimaryKey")
ContainerName = dbutils.widgets.get("ContainerName")
FilePath = dbutils.widgets.get("FilePath")
FileFormat = dbutils.widgets.get("FileFormat")

#DBSchema = 'kh_dev_published_src_cas_db'
#TableName = 'plan_needs_mapping'
#PrimaryKey = 'plan_cd'
#ContainerName = 'wandisco'
#FilePath = '/kh/dev/published/hive/kh_dev_published_src_cas_db/plan_needs_mapping'
#FileFormat = 'orc'

# COMMAND ----------

# DBTITLE 1,Destination Directory Creation
#Run this command cell, then upload metrices received from hive
container = ContainerName
mount_container(container)
tbl_db = DBSchema
tbl_nm = TableName
prim_key = PrimaryKey
mnt_path = dbfs_mount_path+container
date_path = datetime.date.today().strftime('%Y%m%d') #yyyymmdd
dest_path=mnt_path+'/Test_Validation/Advanced_Statistics/'+date_path
dbutils.fs.mkdirs(dest_path)

# COMMAND ----------


file_path= FilePath
file_format = FileFormat
adls_df = load_adls_df(file_path,file_format,container)
if file_format =="orc-acid":
    adls_df = orc_acid_conversion(adls_df)

# COMMAND ----------

file_path= FilePath
file_format = FileFormat
paths = dbutils.fs.ls("/mnt/wandisco/asia")#mnt_path+file_path
display(paths)
for path in paths:
    if path.path.endswith("_orc_acid_version"):
        print(path)

# COMMAND ----------

#adls_df = adls_df.select([when(col(c)=="","null").otherwise(col(c)).alias(c) for c in adls_df.columns])

# COMMAND ----------

adls_df.count()

# COMMAND ----------

#All source metrices
adls_primary_key_df = check_primary_key(adls_df,prim_key, tbl_db, tbl_nm)
adls_cat_df,adls_num_df,  adls_date_df = check_data_types(prim_key, tbl_db, tbl_nm, adls_df)

# COMMAND ----------

adls_primary_key_df=adls_primary_key_df.replace('','null')
adls_cat_df=adls_cat_df.replace('','null')
adls_date_df=adls_date_df.replace('','null')

# COMMAND ----------

adls_primary_key_df.to_csv("/dbfs"+dest_path+f'/Adls_{tbl_nm}_metadata_count.csv',header=True,sep='|')
adls_num_df.to_csv("/dbfs"+dest_path+f'/Adls_{tbl_nm}_num.csv',header=True,sep='|')
adls_cat_df.to_csv("/dbfs"+dest_path+f'/Adls_{tbl_nm}_cat.csv',header=True,sep='|')
adls_date_df.to_csv("/dbfs"+dest_path+f'/Adls_{tbl_nm}_date.csv',header=True,sep='|')

# COMMAND ----------

# DBTITLE 1,Fetch Hive Metrices
#tbl_nm = 'TAMS_AGENTS'
src_primary_key_df = spark.read.option("header","true").option("inferSchema","true").option("delimiter","|").csv(dest_path+f'/Hive_{tbl_nm}_metadata_count.csv').toPandas()
src_cat_df = spark.read.option("header","true").option("inferSchema","true").option("delimiter","|").csv(dest_path+f'/Hive_{tbl_nm}_cat.csv').toPandas()
src_num_df = spark.read.option("header","true").option("inferSchema","true").option("delimiter","|").csv(dest_path+f'/Hive_{tbl_nm}_num.csv').toPandas()
src_date_df = spark.read.option("header","true").option("inferSchema","true").option("delimiter","|").csv(dest_path+f'/Hive_{tbl_nm}_date.csv').toPandas()

# COMMAND ----------

# DBTITLE 1,Merge Source Hive and Target ADLS metrices
#schema_name	table_name	measure	column_value	freq
m_primary = src_primary_key_df.merge(adls_primary_key_df, on=['table_name','measure'], how='outer', suffixes=['', '_tgt'], indicator=True)
#schema_name	table_name	column_name	variable	value
m_num = src_num_df.merge(adls_num_df,on=['table_name','column_name','variable'],how='outer', suffixes=['', '_tgt'], indicator=True)
m_cat = src_cat_df.merge(adls_cat_df,on=["table_name","column_name","column_value"],how='outer', suffixes=['', '_tgt'], indicator=True)
m_date = src_date_df.merge(adls_date_df,on=["table_name","date_type","column_name","column_value"],how='outer', suffixes=['', '_tgt'], indicator=True)

# COMMAND ----------

# DBTITLE 1,Value Diff and Percentage Diff
#m_primary['value_diff'] = m_primary['freq'].sub(m_primary['freq_tgt'])
m_primary['value_diff'] = value_diff(m_primary['freq'],m_primary['freq_tgt'])
m_primary['%diff'] = percentage_changes(m_primary['value_diff'],m_primary['freq'])
# m_cat['value_diff'] = m_cat['freq'].sub(m_cat['freq_tgt'],axis=0)
m_cat['value_diff'] = value_diff(m_cat['freq'],m_cat['freq_tgt'])
m_cat['%diff'] = percentage_changes(m_cat['value_diff'],m_cat['freq'])
m_num['value'] = m_num['value'].astype(float, errors = 'raise').round(4)
m_num['value_tgt'] = m_num['value_tgt'].astype(float, errors = 'raise').round(4)
# m_num['value_diff'] = m_num['value'].sub(m_num['value_tgt'],axis=0)
m_num['value_diff'] = value_diff(m_num['value'],m_num['value_tgt'])
m_num['%diff'] = percentage_changes(m_num['value_diff'],m_num['value'])
m_date['value_diff'] = date_compare(m_date['freq'],m_date['freq_tgt'])

# COMMAND ----------

# DBTITLE 1,Compare ADLS vs Hive save to ADLS loaction
dbutils.fs.mkdirs(dest_path+'/Compare/')
m_primary.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{tbl_nm}_Metadata_count.csv',header=True,sep='|')
m_num.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{tbl_nm}_Numeric_col.csv',header=True,sep='|')
m_cat.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{tbl_nm}_Cat_col.csv',header=True,sep='|')
m_date.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{tbl_nm}_Date_col.csv',header=True,sep='|')

# COMMAND ----------

m_cat[m_cat.column_value=='null']

# COMMAND ----------

m_date[m_date.column_value=='null']
