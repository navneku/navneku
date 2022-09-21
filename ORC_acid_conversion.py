# Databricks notebook source
# MAGIC %run ./02_Utilities

# COMMAND ----------

############################Mount the blob if not mounted#####################################################################
mount_container(wandisco_container_name)

# COMMAND ----------

#Get all the part file folder inside table folder
table_path ='/kh/ldmnonprod/published/hive/kh_dev_published_src_ams_db/MVAMS_AGT_RECRUIT_RELS'
#Get metadata of file in ADLS gen2
ddlSchema = StructType([
StructField('Path',StringType()),
StructField('FileName',StringType()),
StructField('FileSize(Bytes)',IntegerType()),
StructField('Unix_Time',LongType())
])
sklist = dbutils.fs.ls("mnt/wandisco"+table_path)
df_list = spark.createDataFrame(sklist,ddlSchema)
df_list = df_db_list.withColumn("Path",f.regexp_replace(f.col("Path"),'dbfs:',''))
dfpanda = df_list.toPandas()
path_list=[]
for index, rows in dfpanda.iterrows():
    # Create list for the current row
    my_list =rows.Path
      
    # append the list to the final list
    path_list.append(my_list)

# COMMAND ----------

FirstPath = path_list[0]
df_schema = spark.read.format("orc").load(FirstPath)
file_schema = df_schema.schema
df = spark.createDataFrame([],file_schema)
display(df)
for path in path_list:
    SrcFilePath = path
    df_final = spark.read.format("orc").load(SrcFilePath)
    df = df.unionAll(df_final)
    
df.count()

# COMMAND ----------

#Read ORC file
SrcFilePath = '/mnt/wandisco' +"/kh/ldmnonprod/published/hive/kh_dev_published_src_ams_db/MVAMS_AGT_RECRUIT_RELS"
df = spark.read.format("orc").load(SrcFilePath)
df.count()

# COMMAND ----------

#Read the ORC ACID  file- data rows in struct format (always pass the path in which the file is present)
#Get all the part file folder inside table folder
table_path ='/mnt/wandisco/kh/dev/published/hive/kh_dev_published_src_cas_db/plan_needs_mapping'
#Get metadata of file in ADLS gen2
ddlSchema = StructType([
StructField('Path',StringType()),
StructField('FileName',StringType()),
StructField('FileSize(Bytes)',IntegerType()),
StructField('Unix_Time',LongType())
])
sklist = dbutils.fs.ls(table_path)
df_list = spark.createDataFrame(sklist,ddlSchema)
dfpanda = df_list.toPandas()
path_list=[]
for index, rows in dfpanda.iterrows():
    # Create list for the current row
    my_list =rows.Path
      
    # append the list to the final list
    path_list.append(my_list)
FirstPath = path_list[0]
df_schema = spark.read.format("orc").load(FirstPath)
file_schema = df_schema.schema
df = spark.createDataFrame([],file_schema)
for path in path_list:
    SrcFilePath = path
    df_final = spark.read.format("orc").load(SrcFilePath)
    df = df.unionAll(df_final)
display(df)

# COMMAND ----------

#How to convert ORC acid file - Method 1(convert by declaring table schema)
#If schema is not inferred automatically in cmd 4 Declare schema & convert
dfpanda = df.toPandas()
Row_list=[]
for index, rows in dfpanda.iterrows():
    # Create list for the current row
    my_list =rows.row
      
    # append the list to the final list
    Row_list.append(my_list)


    
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

rdd = spark.sparkContext.parallelize(Row_list)

targetDF = spark.createDataFrame(rdd, schema)
targetDF = targetDF.toPandas()
display(targetDF)

# COMMAND ----------

#How to convert ORC acid file - Method 2(infer schema on fly and convert)
dfpanda = df.toPandas()
Row_list=[]
for index, rows in dfpanda.iterrows():
    # Create list for the current row
    my_list =rows.row
      
    # append the list to the final list
    Row_list.append(my_list)
    df_final = spark.createDataFrame(Row_list,[])
targetDF = df_final.toPandas()
display(targetDF)
