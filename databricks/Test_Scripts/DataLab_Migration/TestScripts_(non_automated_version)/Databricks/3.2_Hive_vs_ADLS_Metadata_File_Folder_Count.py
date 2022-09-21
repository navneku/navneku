# Databricks notebook source
# DBTITLE 1,How to Run this notebook
# MAGIC %md
# MAGIC This notebook (Test script) generates metrics like the File/Folder count & compares them between HDFS Vs ADLS
# MAGIC * Prerequisties:
# MAGIC   * Hive metrics must be generated(using jupyter hub/Putty notebook)
# MAGIC * Pass mount path & the Hive metrics file name in cmd 3 , Below is Sample input:
# MAGIC     * mount_path =>''/kh/dev/published/hive/kh_dev_published_src_ams_db' (pass the path for which you need the metrics)
# MAGIC     * Hive_FileFolderCount_FileName => 'Hive_kh_dev_published_src_ams_db_Metadata_File_Folder_Count.csv' (pass the Hive metrics result csv file name)
# MAGIC * To place the Hive result generated in jupyter hub, Run upto cmd 7 (to create current date folder) & place the result in the ADLS (/wandisco/Test_Validation/Metadata/yyyyMMdd/)
# MAGIC * Once the above two are done run the entire notebook 

# COMMAND ----------

# MAGIC %run ./02_Utilities

# COMMAND ----------

# DBTITLE 1,Pass the parameters value here:
#Pass the value of Mount path & Hive File folder count Metrics result file name
mount_path = ''
Hive_FileFolderCount_FileName = ''

#mount_path = '/kh/prod/published/hive/kh_published_cas_db' 
#Hive_FileFolderCount_FileName = 'Hive_kh_published_cas_db_Metadata_File_Folder_Count.csv'


# COMMAND ----------

DateFolder = date.today().strftime("%Y%m%d")
mount_point = dbfs_mount_path + wandisco_container_name + mount_path
FileName = Hive_FileFolderCount_FileName.split(".")[0].replace("Hive_","")
dest_path =  "/Test_Validation/Metadata/"+DateFolder+"/"

# COMMAND ----------

DateFolder,mount_point,FileName,dest_path

# COMMAND ----------

############################Mount the blob if not mounted#####################################################################
if check_if_mounted(dbfs_mount_path + wandisco_container_name) != True :
    mount_adls_container(wandisco_container_name)

# COMMAND ----------

#Run this command to -> Create directory to place the src(Hive) metrics result:
dbutils.fs.mkdirs (dbfs_mount_path + wandisco_container_name + dest_path)
#New path that will be created, will look like : wandisco/Test_Validation/Metadata/yyyyMMdd/ -> current date in yyyyMMdd format
#Place the Hive result csv file on the above mentioned path & run all below codes


# COMMAND ----------

#fetch the src metrics file placed in adls
sourceDF = spark.read.format("csv") \
    .option("inferSchema", "true") \
    .option("header", "true") \
    .option("sep", ",") \
    .load(dbfs_mount_path + wandisco_container_name +dest_path+Hive_FileFolderCount_FileName)
sourceDF =sourceDF.toPandas()

# COMMAND ----------

#display(sourceDF)

# COMMAND ----------

#Function to retrive file & folder count info of all the files in tgt mounted path
rddArr = []

def iterate_path(path):
    total_files = 0
    total_folders = 0
    path_list = dbutils.fs.ls(path)
    if path_list:
        for path_object in path_list:
            tempPath = path_object.path.replace(("dbfs:" + "/mnt/wandisco"), "")
            if str(tempPath).startswith("Test_Validation") == False:
                if path_object.path[-1] == "/":
                    total_folders += 1
                    iterate_path(path_object.path)
                else:
                    total_files += 1
    newPath = (path.replace(("dbfs:" + "/mnt/wandisco"), ""))
    if(newPath == mount_point):
        newPath = mount_point.replace("/mnt/wandisco","")+"/"
    rddArr.append((newPath, total_folders, total_files))

iterate_path(mount_point)

# COMMAND ----------

#form the tgt df from the above result & save to Test_Validation current date folder
schema = StructType([StructField('Path', StringType(), False),
                            StructField('FolderCount', IntegerType(), False),
                            StructField('FileCount', IntegerType(), False)])

rdd = spark.sparkContext.parallelize(rddArr)

targetDF = spark.createDataFrame(rdd, schema)
targetDF = targetDF.toPandas()
targetDF.to_csv('/dbfs' + dbfs_mount_path + wandisco_container_name + dest_path + 'ADLS_' + FileName + '.csv',header=True)

# COMMAND ----------

#display(targetDF)


# COMMAND ----------

#Form the compare df
CompareDF = sourceDF.merge(targetDF, on="Path",how='left',suffixes=['', '_tgt'], indicator=True)

# COMMAND ----------

#Create the Value Diff metrics after comparing src & tgt
CompareDF['FolderCountValueDiff'] = CompareDF['FolderCount'].sub(CompareDF['FolderCount_tgt'])
CompareDF['FolderCount%diff'] = percentage_change(CompareDF['FolderCount'],CompareDF['FolderCount_tgt'])
CompareDF['FileCountValueDiff'] = CompareDF['FileCount'].sub(CompareDF['FileCount_tgt'])
CompareDF['FileCount%diff'] = percentage_change(CompareDF['FileCount'],CompareDF['FileCount_tgt'])

# COMMAND ----------

#display(CompareDF)

# COMMAND ----------

# Save the compare result into Test_Validation current date folder as csv file
CompareDF.to_csv('/dbfs' + dbfs_mount_path + wandisco_container_name + dest_path + 'Compare_' + FileName + '.csv',header=True)
