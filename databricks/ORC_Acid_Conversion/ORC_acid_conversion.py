# Databricks notebook source
#Place the "01_Initialize" and "02_Utilities" files in the same workspace folder as this notebook

# COMMAND ----------

# MAGIC %run ./02_Utilities

# COMMAND ----------

#Note: To read non transactional table ORC files use cmd 5   
#Note: Tansactional table - ORC ACID - if there is only one part folder,always pass the path in which the file is present and use cmd 6(uncomment it)
# cmd 8 & 9 are for converting transactional tbl struct type rows to columnar
#Note: Tansactional table - ORC ACID - if there are multiple part files sub folders present in table folder , pass table path and use cmd 7
#Note: If method 1 (cmd 8) fails to infer table schema automatically from the file, use Method 2 (cmd 9- declare your table schema) for conversion

# COMMAND ----------

#Pass container & path here
Container ='datalab'
TblPath='/mnt/datalab/Project/Read Files/ORC-Acid-Multiplesubfolders/'
#TblPath = /mnt/<container>/<Path> - change the container & Path accordingly


# COMMAND ----------

adls_primary_key_df.to_csv("/dbfs"+dest_path+f'/Adls_{tbl_nm}_metadata_count.csv',header=True)
adls_num_df.to_csv("/dbfs"+dest_path+f'/Adls_{tbl_nm}_num.csv',header=True)
adls_cat_df.to_csv("/dbfs"+dest_path+f'/Adls_{tbl_nm}_cat.csv',header=True)
adls_date_df.to_csv("/dbfs"+dest_path+f'/Adls_{tbl_nm}_date.csv',header=True)

# COMMAND ----------

############################Mount the blob if not mounted#####################################################################
mount_container(Container)

# COMMAND ----------

# DBTITLE 1,ORC File
#Read ORC file- Example of normal ORC file
#TblPath = '/mnt/wandisco' +"/kh/ldmnonprod/published/hive/kh_dev_published_src_ams_db/MVAMS_AGT_RECRUIT_RELS"
#df = spark.read.format("orc").load(TblPath)
#display(df)

# COMMAND ----------

# DBTITLE 1,ORC ACID - with one part folder
#Read the ORC ACID  file- data rows in struct format (if there is only one part folder,always pass the path in which the file is present in cmd2)
# sample path , TblPath ='mnt/wandisco/kh/dev/published/hive/kh_dev_published_src_cas_db/plan_needs_mapping/delta_0000001_0000001_0000/'
#df = spark.read.format("orc").load(TblPath)
#display(df)

# COMMAND ----------

# DBTITLE 1,ORC ACID with multiple part folder
#Read the ORC ACID  file- data rows in struct format (if there are multiple part folders)
df = spark.read.format("orc").option("recursiveFileLookup","True").load(TblPath)
display(df)

# COMMAND ----------

# DBTITLE 1,Method 1 - databricks infers table schema automatically & converts
#How to convert ORC acid file - Method 1(infer schema on fly and convert)
Row_list=[]
Row_list = df.toPandas()['row']
targetDF = spark.createDataFrame(Row_list,[])
display(targetDF)
targetDF.count()

# COMMAND ----------

# DBTITLE 1,Method 2 - Declare table schema & convert (if above method fails)
#How to convert ORC acid file - Method 2(convert by declaring table schema)
#If schema is not inferred automatically in method 1  Declare table schema & convert
Row_list=[]
Row_list = df.toPandas()['row']


#Declare Table schema example as below:
schema = StructType([StructField('effective_date', StringType(), False),
StructField('effective_qtr', StringType(), False),
StructField('product_nm', StringType(), False),
StructField('plan_cd', StringType(), False),
StructField('cvg_typ', StringType(), False),
StructField('product_name', StringType(), False),
StructField('product', StringType(), False),
StructField('benefit_type', StringType(), False),
StructField('customer_needs', StringType(), False),
StructField('par_np_ind', StringType(), False),
StructField('external_lob', StringType(), False),
StructField('lob', StringType(), False),
StructField('nbv_margin_agency', DoubleType(), False),
StructField('nbv_margin_banca_other_banks', DoubleType(), False),
StructField('nbv_margin_banca_aba', DoubleType(), False),
StructField('nbv_margin_banca_spn', DoubleType(), False),
StructField('nbv_margin_direct', DoubleType(), False)])

targetDF = spark.createDataFrame(Row_list, schema)
display(targetDF)
targetDF.count()
