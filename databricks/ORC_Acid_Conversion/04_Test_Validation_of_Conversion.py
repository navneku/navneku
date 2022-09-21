# Databricks notebook source
# MAGIC %run ./02_Utilities

# COMMAND ----------

#Pass container & path 
Container = 'wandisco'
tblPath = '/kh/dev/published/hive/kh_dev_published_src_ams_db/test_tbl/'
TblmountPath='/mnt/'+Container+tblPath
MountPoint = '/mnt/'+Container+'/'

ParquetPath = 'ORC_ACID_to_Parquet_Conversion'
print(TblmountPath)
print(MountPoint + ParquetPath + tblPath)

# COMMAND ----------

############################Mount the blob if not mounted#####################################################################
mount_container(Container)

# COMMAND ----------

# DBTITLE 1,Check list of paths inside tbl folder
#Get all path details that contains ORC Acid files inside the mounted path
paths = get_dir_content(TblmountPath)
File_Path=[]
#Filter paths that contain _orc_acid_version
for p in paths:
    if p.endswith('_orc_acid_version'):
        File_Path.append(p.replace("dbfs:","").replace('_orc_acid_version',''))
path_list=[]
path_list = list(set(File_Path))
print(path_list)
#print(len(path_list))

# COMMAND ----------

# DBTITLE 1,Read the table ORC Acid files 
Row_list=[]
df = spark.read.format("orc").option("recursiveFileLookup","True").load(TblmountPath)
rdd = df.rdd.map(lambda x: x[-1])
schema_df = rdd.toDF(sampleRatio=0.1)
my_schema=list(schema_df.schema)
null_cols = []
# iterate over schema list to filter for NullType columns
for st in my_schema:
    if str(st.dataType) == 'NullType' or  str(st.dataType) == 'NoneType':
        null_cols.append(st)
for ncol in null_cols:
    mycolname = str(ncol.name)
    schema_df = schema_df \
        .withColumn(mycolname, schema_df[mycolname].cast('string'))
fileschema = schema_df.schema
targetDF = spark.createDataFrame(rdd,fileschema)
display(targetDF)
targetDF.count()

# COMMAND ----------

# DBTITLE 1,Read the table parquet file
#to read the parquet files of a particular tbl
basepath = MountPoint +'ORC_ACID_to_Parquet_Conversion'+tblPath
paths = [basepath+'/*.parquet']
d= spark.read.option("basePath",basepath).parquet(*paths)
display(d)
d.count()
