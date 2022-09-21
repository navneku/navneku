# Databricks notebook source
# MAGIC %md
# MAGIC This notebook will create advanced metrics for table Synapse and compare it with hive mertics
# MAGIC * Prerequisties:
# MAGIC   * Hive metrics must be generated(using jupyter hub/Putty notebook)
# MAGIC * After passing parameters & running till command 4:
# MAGIC   * Pass parameters in cmd 3, below are the samples:
# MAGIC     * Container : dev
# MAGIC     * DBSchema : kh_dev_published_src_cas_db
# MAGIC     * PrimaryKey : plan_cd (# primary key for that table)
# MAGIC     * TableName : plan_needs_mapping (name of the table)
# MAGIC   * upload the hive metrics file in the file location created in command 4 (container/Test_Validation/Advanced_Statistics/<schema.table_name>/yyyMMdd/)
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


DBSchema = dbutils.widgets.get("DBSchema")
TableName = dbutils.widgets.get("TableName")
PrimaryKey = dbutils.widgets.get("PrimaryKey")
ContainerName = dbutils.widgets.get("ContainerName")
#DBSchema = 'curated'
#TableName = 'persistency_eda_lapse_dim'
#PrimaryKey = 'pol_num'
#Container = 'dev'

# COMMAND ----------

# DBTITLE 1,Make destination directory before dropping Hive metrics file
container = ContainerName
mount_container(container)
tbl_db = DBSchema
tbl_nm = TableName
prim_key = PrimaryKey
mnt_path = dbfs_mount_path+container
date_path = date.today().strftime('%Y%m%d') #yyyy/mm/dd
dest_path=mnt_path+'/Test_Validation/Advanced_Statistics/'+tbl_db+'.'+tbl_nm+'/'+date_path
dbutils.fs.mkdirs(dest_path)

# COMMAND ----------

# DBTITLE 1,Create Synapse Dataframe
tbl_name = tbl_db+'.'+tbl_nm
syn_df = synapse_table_df(tbl_name)

# COMMAND ----------

display(syn_df)

# COMMAND ----------

# DBTITLE 1,Compute Synapse Metrics
#All source metrices
syn_primary_key_df = check_primary_key(syn_df,prim_key, tbl_db, tbl_nm)
syn_cat_df,syn_num_df, syn_date_df = check_data_types(prim_key, tbl_db, tbl_nm, syn_df)

# COMMAND ----------

# DBTITLE 1,Save Synapse Metrics to ADLS 
syn_primary_key_df.to_csv("/dbfs"+dest_path+'/Synapse_primary_key.csv',header=True)
syn_num_df.to_csv("/dbfs"+dest_path+'/Synapse_num.csv',header=True)
syn_cat_df.to_csv("/dbfs"+dest_path+'/Synapse_cat.csv',header=True)
syn_date_df.to_csv("/dbfs"+dest_path+'/Synapse_date.csv',header=True)

# COMMAND ----------

# DBTITLE 1,Fetch Hive Metrices
src_primary_key_df = spark.read.option("header","true").option("inferSchema","true").csv(dest_path+'/Hive_primary_key.csv').toPandas()
src_cat_df = spark.read.option("header","true").option("inferSchema","true").csv(dest_path+'/Hive_cat.csv').toPandas()
src_num_df = spark.read.option("header","true").option("inferSchema","true").csv(dest_path+'/Hive_num.csv').toPandas()
src_date_df = spark.read.option("header","true").option("inferSchema","true").csv(dest_path+'/Hive_date.csv').toPandas()

# COMMAND ----------

# DBTITLE 1,Merge Source Hive and Target Synapse metrices
#schema_name	table_name	measure	column_value	freq
m_primary = src_primary_key_df.merge(syn_primary_key_df, on=['schema_name','table_name','measure'], how='left', suffixes=['', '_tgt'], indicator=True)
#schema_name	table_name	column_name	variable	value
m_num = src_num_df.merge(syn_num_df,on=['schema_name','table_name','column_name','variable'],how='left', suffixes=['', '_tgt'], indicator=True)
m_cat = src_cat_df.merge(syn_cat_df,on=["schema_name","table_name","column_name","column_value"],how='left', suffixes=['', '_tgt'], indicator=True)
m_date = src_date_df.merge(syn_date_df,on=["schema_name","table_name","date_type","column_name","column_value"],how='left', suffixes=['', '_tgt'], indicator=True)

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

# DBTITLE 1,Compare Synapse vs Hive save to ADLS loaction
dbutils.fs.mkdirs(dest_path+'/Diff/')
m_primary.to_csv("/dbfs"+dest_path+'/Diff/Primary_key_diff.csv',header=True)
m_num.to_csv("/dbfs"+dest_path+'/Diff/Numeric_col_diff.csv',header=True)
m_cat.to_csv("/dbfs"+dest_path+'/Diff/Cat_col_diff.csv',header=True)
m_date.to_csv("/dbfs"+dest_path+'/Diff/Date_col_diff.csv',header=True)
