# Databricks notebook source
# MAGIC %md
# MAGIC This notebook will create advanced metrics for table file in ADLS and compare it with hive mertics
# MAGIC * This Notebook is invoked by 1_Oracle_Advanced_Statistics_Main.
# MAGIC * This notebook can also  run individually if you need Advanced stats metrics for Table.
# MAGIC 
# MAGIC * Prerequisties:
# MAGIC   * Hive metrics must be generated(using jupyter hub/Putty notebook)
# MAGIC   
# MAGIC * To run this notebook individually for getting Advanced stats for one particular table, follow the below steps:
# MAGIC   * Run cmd 3, widgets will appear on the top with below tags, fill them, below are the samples:
# MAGIC      * ContainerName : dev
# MAGIC      * DBSchema : curated
# MAGIC      * PrimaryKey : pol_num (# primary key for that table)
# MAGIC      * TableName : persistency_eda_lapse_dim (name of the table)
# MAGIC   * Pass the values in the above widgets, run cmd 3 again.
# MAGIC   * Run upto cmd 4 & upload the hive metrics file in the file location created by running command 4 (wandisco/Test_Validation/Advanced_Statistics/yyyMMdd/)
# MAGIC   * Once the above two are done run the entire notebook 

# COMMAND ----------

# MAGIC %run ../02_Utilities

# COMMAND ----------

# DBTITLE 1,Pass the parameters value here
dbutils.widgets.removeAll()
dbutils.widgets.text("DBSchema","")
dbutils.widgets.text("TableName","")
dbutils.widgets.text("PrimaryKey","")
dbutils.widgets.text("ContainerName","")

DBSchema = dbutils.widgets.get("DBSchema")
TableName = dbutils.widgets.get("TableName")
PrimaryKey = dbutils.widgets.get("PrimaryKey")
Container = dbutils.widgets.get("ContainerName")
#DBSchema = 'curated'
#TableName = 'persistency_eda_lapse_dim'
#PrimaryKey = 'pol_num'
#Container = 'dev'

# COMMAND ----------

# DBTITLE 1,Make destination directory before dropping Hive metrics file
#Run this command cell, then upload metrices received from hive
container = Container
mount_container(container)
Oracle_tbl_db,tbl_db = DBSchema,DBSchema
Oracle_tbl_nm,tbl_nm = TableName,TableName
prim_key = PrimaryKey
mnt_path = dbfs_mount_path+container
date_path = date.today().strftime('%Y%m%d') #yyyy/mm/dd
dest_path=mnt_path+'/Test_Validation/Oracle/Advanced_Statistics/'+date_path
tbl_adls_file_path= '/Published/KH/Master/Oracle/'+TableName
file_format = 'parquet'
dbutils.fs.mkdirs(dest_path)
print(dest_path)
print(tbl_adls_file_path)

# COMMAND ----------

# DBTITLE 1,Create Oracle Dataframe
tbl_name = Oracle_tbl_db+'.'+Oracle_tbl_nm
Oracle_df = oracle_table_df(tbl_name)
#display(Oracle_df)
Oracle_df.count()

# COMMAND ----------

df = spark.read \
    .format("jdbc") \
    .option("url", oracle_url) \
    .option('query','select * from ' +tbl_name)\
    .option("user", oracle_username) \
    .option("password", oracle_password) \
    .option("driver", "oracle.jdbc.driver.OracleDriver") \
    .load()

# COMMAND ----------

display(df)
df.count()

# COMMAND ----------

# DBTITLE 1,Compute Oracle Metrics
#All source metrices
Oracle_primary_key_df = check_primary_key(Oracle_df,prim_key, Oracle_tbl_db, Oracle_tbl_nm)
Oracle_cat_df,Oracle_num_df, Oracle_date_df = check_data_types(prim_key, Oracle_tbl_db, Oracle_tbl_nm, Oracle_df)

# COMMAND ----------

# DBTITLE 1,Save Oracle Metrics to ADLS 
Oracle_primary_key_df.to_csv("/dbfs"+dest_path+f'/Oracle_{Oracle_tbl_nm}_metadata_count.csv',header=True,sep='|')
Oracle_num_df.to_csv("/dbfs"+dest_path+f'/Oracle_{Oracle_tbl_nm}_num.csv',header=True,sep='|')
Oracle_cat_df.to_csv("/dbfs"+dest_path+f'/Oracle_{Oracle_tbl_nm}_cat.csv',header=True,sep='|')
Oracle_date_df.to_csv("/dbfs"+dest_path+f'/Oracle_{Oracle_tbl_nm}_date.csv',header=True,sep='|')

# COMMAND ----------

# DBTITLE 1,Create ADLS Dataframe

adls_df = load_adls_df(tbl_adls_file_path,file_format)
display(adls_df)
adls_df.count()

# COMMAND ----------

# DBTITLE 1,Compute ADLS Metrics
adls_primary_key_df = check_primary_key(adls_df,prim_key, tbl_db, tbl_nm)
adls_cat_df,adls_num_df,adls_date_df = check_data_types(prim_key, tbl_db, tbl_nm, adls_df)

# COMMAND ----------

# DBTITLE 1,Save ADLS Metrics to ADLS
adls_primary_key_df.to_csv("/dbfs"+dest_path+f'/ADLS_{tbl_nm}_metadata_count.csv',header=True,sep='|')
adls_num_df.to_csv("/dbfs"+dest_path+f'/ADLS_{tbl_nm}_num.csv',header=True,sep='|')
adls_cat_df.to_csv("/dbfs"+dest_path+f'/ADLS_{tbl_nm}_cat.csv',header=True,sep='|')
adls_date_df.to_csv("/dbfs"+dest_path+f'/ADLS_{tbl_nm}_date.csv',header=True,sep='|')

# COMMAND ----------

# DBTITLE 1,Merge Source Hive and Target Oracle metrices
#schema_name	table_name	measure	column_value	freq
m_primary = Oracle_primary_key_df.merge(adls_primary_key_df, on=['table_name','measure'], how='outer', suffixes=['', '_tgt'], indicator=True)
#schema_name	table_name	column_name	variable	value
m_num = Oracle_num_df.merge(adls_num_df,on=['table_name','column_name','variable'],how='outer', suffixes=['', '_tgt'], indicator=True)
m_cat = Oracle_cat_df.merge(adls_cat_df,on=["table_name","column_name","column_value"],how='outer', suffixes=['', '_tgt'], indicator=True)
m_date = Oracle_date_df.merge(adls_date_df,on=["table_name","date_type","column_name","column_value"],how='outer', suffixes=['', '_tgt'], indicator=True)

# COMMAND ----------

# DBTITLE 1,Value Diff and Percentage Diff
#m_primary['value_diff'] = m_primary['freq'].sub(m_primary['freq_tgt'])
m_primary['value_diff'] = value_diff(m_primary['freq'],m_primary['freq_tgt'])
m_primary['%diff'] = percentage_change(m_primary['value_diff'],m_primary['freq'])
# m_cat['value_diff'] = m_cat['freq'].sub(m_cat['freq_tgt'],axis=0)
m_cat['value_diff'] = value_diff(m_cat['freq'],m_cat['freq_tgt'])
m_cat['%diff'] = percentage_change(m_cat['value_diff'],m_cat['freq'])
m_num['value'] = m_num['value'].astype(float, errors = 'raise').round(4)
m_num['value_tgt'] = m_num['value_tgt'].astype(float, errors = 'raise').round(4)
m_num['value_diff'] = value_diff(m_num['value'],m_num['value_tgt'])
m_num['%diff'] = percentage_change(m_num['value_diff'],m_num['value'])
m_date['value_Match'] = date_compare(m_date['freq'],m_date['freq_tgt'])

# COMMAND ----------

# DBTITLE 1,Compare Oracle vs Hive save to ADLS location
dbutils.fs.mkdirs(dest_path+'/Compare/')
m_primary.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{Oracle_tbl_nm}_Metadata_count.csv',header=True,sep='|')
m_num.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{Oracle_tbl_nm}_Numeric_col.csv',header=True,sep='|')
m_cat.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{Oracle_tbl_nm}_Cat_col.csv',header=True,sep='|')
m_date.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{Oracle_tbl_nm}_Date_col.csv',header=True,sep='|')

# COMMAND ----------

m_primary

# COMMAND ----------

m_cat

# COMMAND ----------

m_num

# COMMAND ----------

m_date
