# Databricks notebook source
# DBTITLE 1,Introduction
# MAGIC %md
# MAGIC * This notebook Converts all (Transactional property enabled tables) ORC ACID files present in the path passed "{container}/{mount_path}/" to Parquet files and saves to - "{container}/ORC_ACID_to_Parquet_Conversion/{mount_path}/" location
# MAGIC * InputParameter: pass the comma separated value in widget in json format: eg. {"container":"wandisco","mount_path":"/kh/"}
# MAGIC  
# MAGIC    * container : Pass adls container name in which the ORC ACID files are present. eg.-  wandisco
# MAGIC    * mount_path : Pass the path for which you want to execute the notebook for conversion eg, /kh/dev/ (mount path must start and end with '/')
# MAGIC * We can manually run this notebook or Schedule a Job to run this notebook configuring it for required container/mount_path

# COMMAND ----------

# MAGIC %run ./02_Utilities

# COMMAND ----------

#Pass container & path 
dbutils.widgets.removeAll()
dbutils.widgets.text("InputParameter","")
InputParameter = dbutils.widgets.get("InputParameter")

# Convenience function for turning JSON string into dataframe.
def jsonToDataFrame(json, schema=None):
    reader = spark.read
    if schema:
        reader.schema(schema)
    return reader.json(sc.parallelize([json]))
dfJson = jsonToDataFrame(InputParameter)
display(dfJson)
Container = dfJson.select("container").head()[0]
mount_path = dfJson.select("mount_path").head()[0]
MountPoint = dbfs_mount_path + Container+'/'
MountPath = dbfs_mount_path + Container +mount_path
ParquetPath = 'ORC_ACID_to_Parquet_Conversion'
print(MountPath)
print(MountPoint + ParquetPath + mount_path)

# COMMAND ----------

############################Mount the blob if not mounted#####################################################################
mount_container( Container)

# COMMAND ----------

# DBTITLE 1,Clean up existing parquet path
if folder_exist(MountPoint + ParquetPath + mount_path):
    path = get_dir_content(MountPoint + ParquetPath + mount_path)
    for p in reversed(path):
        dbutils.fs.rm(p,True)

# COMMAND ----------

# DBTITLE 1,Get all ORC ACID Paths
#Get all path details that contains ORC Acid files inside the mounted path
paths = get_dir_content(MountPath)
File_Path=[]
#Filter paths that contain _orc_acid_version
for p in paths:
    if p.endswith('_orc_acid_version'):
        File_Path.append(p.replace("dbfs:","").replace('_orc_acid_version',''))
path_list=[]
path_list = list(set(File_Path))
#print(path_list)
#print(len(path_list))

# COMMAND ----------

# DBTITLE 1,Read the ORC Acid files and convert to Parquet
Row_list=[]
if len(path_list) > 0:
    for path in path_list:
        Row_List=[]
        df = spark.read.format("orc").option("recursiveFileLookup","True").load(path)
        print(path)
        ParquetDestPath = MountPoint + ParquetPath + path.replace(dbfs_mount_path + Container,'')
        rdd = df.rdd.map(lambda x: x[-1])
        schema_df = rdd.toDF(sampleRatio=0.5)
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
        #targetDF.write.mode("overwrite").parquet(ParquetDestPath)
