# Databricks notebook source
# DBTITLE 1,How To  Run This Notebook
# MAGIC %md
# MAGIC This notebook will create advanced metrics for table file in ADLS and compare it with hive mertics
# MAGIC * Prerequisties:
# MAGIC   * Hive metrics must be generated(using jupyter hub/Putty notebook)
# MAGIC * After passing parameters & running till command 4:
# MAGIC   * Pass parameters in cmd 3 , below are the samples:
# MAGIC     * ContainerName : wandisco
# MAGIC     * DBSchema : kh_dev_published_src_cas_db
# MAGIC     * FileFormat : orc (generally  it will be orc, parquet, csv  else give 'orc-acid' if its table file with transactional property enabled)
# MAGIC     * FilePath : /kh/dev/published/hive/kh_dev_published_src_cas_db/plan_needs_mapping/delta_0000001_0000001_0000 (#give the path where final file is present )
# MAGIC     * PrimaryKey : plan_cd (# primary key for that table)
# MAGIC     * TableName : plan_needs_mapping (name of the table)
# MAGIC   * upload the hive metrics file in the file location created in command 4 (wandisco/Test_Validation/Advanced_Statistics/<schema.table_name>/yyyMMdd/)
# MAGIC   * Once the above two are done run the entire notebook 

# COMMAND ----------

# MAGIC %run ./02_Utilities

# COMMAND ----------

# DBTITLE 1,Pass the parameters value here:
DBSchema = ''
TableName = ''
PrimaryKey = ''
ContainerName = ''
FilePath = ''
FileFormat = ''

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
dest_path=mnt_path+'/Test_Validation/Advanced_Statistics/'+tbl_db+'.'+tbl_nm+'/'+date_path
dbutils.fs.mkdirs(dest_path)

# COMMAND ----------


file_path= FilePath
file_format = FileFormat
adls_df = load_adls_df(file_path,file_format,container)
if file_format =="orc-acid":
    adls_df = orc_acid_conversion(adls_df)

# COMMAND ----------

display(adls_df)

# COMMAND ----------

#All source metrices
adls_primary_key_df = check_primary_key(adls_df,prim_key, tbl_db, tbl_nm)
adls_cat_df,adls_num_df,  adls_date_df = check_data_types(prim_key, tbl_db, tbl_nm, adls_df)

# COMMAND ----------

adls_primary_key_df.to_csv("/dbfs"+dest_path+'/Adls_primary_key.csv',header=True)
adls_num_df.to_csv("/dbfs"+dest_path+'/Adls_num.csv',header=True)
adls_cat_df.to_csv("/dbfs"+dest_path+'/Adls_cat.csv',header=True)
adls_date_df.to_csv("/dbfs"+dest_path+'/Adls_date.csv',header=True)

# COMMAND ----------

# DBTITLE 1,Fetch Hive Metrices
src_primary_key_df = spark.read.option("header","true").option("inferSchema","true").csv(dest_path+'/Hive_primary_key.csv').toPandas()
src_cat_df = spark.read.option("header","true").option("inferSchema","true").csv(dest_path+'/Hive_cat.csv').toPandas()
src_num_df = spark.read.option("header","true").option("inferSchema","true").csv(dest_path+'/Hive_num.csv').toPandas()
src_date_df = spark.read.option("header","true").option("inferSchema","true").csv(dest_path+'/Hive_date.csv').toPandas()

# COMMAND ----------

# DBTITLE 1,Merge Source Hive and Target ADLS metrices
#schema_name	table_name	measure	column_value	freq
m_primary = src_primary_key_df.merge(adls_primary_key_df, on=['schema_name','table_name','measure'], how='left', suffixes=['', '_tgt'], indicator=True)
#schema_name	table_name	column_name	variable	value
m_num = src_num_df.merge(adls_num_df,on=['schema_name','table_name','column_name','variable'],how='left', suffixes=['', '_tgt'], indicator=True)
m_cat = src_cat_df.merge(adls_cat_df,on=["schema_name","table_name","column_name","column_value"],how='left', suffixes=['', '_tgt'], indicator=True)
m_date = src_date_df.merge(adls_date_df,on=["schema_name","table_name","date_type","column_name","column_value"],how='left', suffixes=['', '_tgt'], indicator=True)

# COMMAND ----------

# DBTITLE 1,Value Diff and Percentage Diff
m_primary['value_diff'] = m_primary['freq'].sub(m_primary['freq_tgt'])
m_primary['%diff'] = percentage_change(m_primary['freq'],m_primary['freq_tgt'])
m_cat['value_diff'] = m_cat['freq'].sub(m_cat['freq_tgt'],axis=0)
m_cat['%diff'] = percentage_change(m_cat['freq'],m_cat['freq_tgt'])
m_num['value_tgt'] = m_num['value_tgt'].astype(float, errors = 'raise')
m_num['value_diff'] = m_num['value'].sub(m_num['value_tgt'],axis=0)
m_num['%diff'] = percentage_change(m_num['value'],m_num['value_tgt'])
m_date['value_diff'] = m_date['freq'].sub(m_date['freq_tgt'],axis=0)
m_date['%diff'] = percentage_change(m_date['freq'],m_date['freq_tgt'])

# COMMAND ----------

# DBTITLE 1,Compare ADLS vs Hive save to ADLS loaction
dbutils.fs.mkdirs(dest_path+'/Diff/')
m_primary.to_csv("/dbfs"+dest_path+'/Diff/Primary_key_diff.csv',header=True)
m_num.to_csv("/dbfs"+dest_path+'/Diff/Numeric_col_diff.csv',header=True)
m_cat.to_csv("/dbfs"+dest_path+'/Diff/Cat_col_diff.csv',header=True)
m_date.to_csv("/dbfs"+dest_path+'/Diff/Date_col_diff.csv',header=True)
