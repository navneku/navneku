# Databricks notebook source
# MAGIC %md
# MAGIC This notebook will create advanced metrics for table file in ADLS and compare it with hive mertics
# MAGIC * This Notebook is invoked by 3.1curated_Advanced_Statistics_Main.
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
# MAGIC      * TableName : persistency_eda_lapse_dim/persistency_eda_persist_tbl (name of the table)
# MAGIC   * Pass the values in the above widgets, run cmd 3 again.
# MAGIC   * Run upto cmd 4 & upload the hive metrics file in the file location created by running command 4 (wandisco/Test_Validation/Advanced_Statistics/yyyMMdd/)
# MAGIC   * Once the above two are done run the entire notebook 

# COMMAND ----------

# MAGIC %run ./02_Utilities

# COMMAND ----------

# DBTITLE 1,Pass the parameters value here
dbutils.widgets.removeAll()
dbutils.widgets.text("DBSchema","")
dbutils.widgets.text("TableName","")
dbutils.widgets.text("PrimaryKey","")
dbutils.widgets.text("ContainerName","")
dbutils.widgets.text("CuratedFlag","")

DBSchema = dbutils.widgets.get("DBSchema")
TableName = dbutils.widgets.get("TableName")
PrimaryKey = dbutils.widgets.get("PrimaryKey")
Container = dbutils.widgets.get("ContainerName")
isCurated = dbutils.widgets.get("CuratedFlag")
#DBSchema = 'curated'
#TableName = 'persistency_eda_lapse_dim'
#PrimaryKey = 'pol_num'
#Container = 'dev'

# COMMAND ----------

# DBTITLE 1,Make destination directory before dropping Hive metrics file
#Run this command cell, then upload metrices received from hive
container = Container
mount_container(container)
syn_tbl_db,hive_tbl_db = DBSchema,DBSchema
syn_tbl_nm,hive_tbl_nm = TableName,TableName
prim_key = PrimaryKey
mnt_path = dbfs_mount_path+container
date_path = date.today().strftime('%Y%m%d') #yyyy/mm/dd
dest_path=mnt_path+'/Test_Validation/Advanced_Statistics/'+date_path
dbutils.fs.mkdirs(dest_path)

# COMMAND ----------

# DBTITLE 1,Create Synapse Dataframe
if isCurated=="1":
    syn_tbl_db = syn_tbl_db.replace("published","curated")
tbl_name = syn_tbl_db+'.'+syn_tbl_nm
syn_df = synapse_table_df(tbl_name)
syn_df=syn_df.select([when(col(c)=="","null").otherwise(col(c)).alias(c) for c in syn_df.columns])

# COMMAND ----------

syn_df.count()

# COMMAND ----------

print(dest_path)

# COMMAND ----------

# DBTITLE 1,Compute Synapse Metrics
#All source metrices
syn_primary_key_df = check_primary_key(syn_df,prim_key, syn_tbl_db, syn_tbl_nm)
syn_cat_df,syn_num_df, syn_date_df = check_data_types(prim_key, syn_tbl_db, syn_tbl_nm, syn_df)

# COMMAND ----------

syn_primary_key_df=syn_primary_key_df.replace('','null')
syn_cat_df=syn_cat_df.replace('','null')
syn_date_df=syn_date_df.replace('','null')

# COMMAND ----------

# DBTITLE 1,Save Synapse Metrics to ADLS 
syn_primary_key_df.to_csv("/dbfs"+dest_path+f'/Synapse_{syn_tbl_nm}_metadata_count.csv',header=True,sep='|')
syn_num_df.to_csv("/dbfs"+dest_path+f'/Synapse_{syn_tbl_nm}_num.csv',header=True,sep='|')
syn_cat_df.to_csv("/dbfs"+dest_path+f'/Synapse_{syn_tbl_nm}_cat.csv',header=True,sep='|')
syn_date_df.to_csv("/dbfs"+dest_path+f'/Synapse_{syn_tbl_nm}_date.csv',header=True,sep='|')

# COMMAND ----------

# DBTITLE 1,Fetch Hive Metrices
src_primary_key_df = spark.read.option("header","true").option("inferSchema","true").option("delimiter","|").option("nullValues",None).csv(dest_path+f'/Hive_{hive_tbl_nm}_metadata_count.csv').toPandas()
src_cat_df = spark.read.option("header","true").option("inferSchema","true").option("delimiter","|").option("nullValues",None).csv(dest_path+f'/Hive_{hive_tbl_nm}_cat.csv').toPandas()
src_num_df = spark.read.option("header","true").option("inferSchema","true").option("delimiter","|").option("nullValues",None).csv(dest_path+f'/Hive_{hive_tbl_nm}_num.csv').toPandas()
src_date_df = spark.read.option("header","true").option("inferSchema","true").option("delimiter","|").option("nullValues",None).csv(dest_path+f'/Hive_{hive_tbl_nm}_date.csv').toPandas()

# COMMAND ----------

# DBTITLE 1,Merge Source Hive and Target Synapse metrices
#schema_name	table_name	measure	column_value	freq
m_primary = src_primary_key_df.merge(syn_primary_key_df, on=['table_name','measure'], how='outer', suffixes=['', '_tgt'], indicator=True)
#schema_name	table_name	column_name	variable	value
m_num = src_num_df.merge(syn_num_df,on=['table_name','column_name','variable'],how='outer', suffixes=['', '_tgt'], indicator=True)
m_cat = src_cat_df.merge(syn_cat_df,on=["table_name","column_name","column_value"],how='outer', suffixes=['', '_tgt'], indicator=True)
m_date = src_date_df.merge(syn_date_df,on=["table_name","date_type","column_name","column_value"],how='outer', suffixes=['', '_tgt'], indicator=True)

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
# m_num['value_diff'] = m_num['value'].sub(m_num['value_tgt'],axis=0)
m_num['value_diff'] = value_diff(m_num['value'],m_num['value_tgt'])
m_num['%diff'] = percentage_change(m_num['value_diff'],m_num['value'])
m_date['value_diff'] = date_compare(m_date['freq'],m_date['freq_tgt'])

# COMMAND ----------

# DBTITLE 1,Compare Synapse vs Hive save to ADLS location
dbutils.fs.mkdirs(dest_path+'/Compare/')
m_primary.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{syn_tbl_nm}_Metadata_count.csv',header=True,sep='|')
m_num.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{syn_tbl_nm}_Numeric_col.csv',header=True,sep='|')
m_cat.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{syn_tbl_nm}_Cat_col.csv',header=True,sep='|')
m_date.to_csv("/dbfs"+dest_path+f'/Compare/Compare_{syn_tbl_nm}_Date_col.csv',header=True,sep='|')

# COMMAND ----------

m_cat[m_cat.column_value=='null']

# COMMAND ----------

m_date[m_date.column_value=='null']

# COMMAND ----------


