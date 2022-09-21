# Databricks notebook source
# DBTITLE 1,How to Run this notebook
# MAGIC %md
# MAGIC * This notebook (Test script) generates ADLS metrics like the File/Folder count for given path & compares them between HDFS Vs ADLS.
# MAGIC * This Notebook is invoked by 3.1_File_Folder_Size_Count_Metadata_Main.
# MAGIC * This notebook can also  run individually if you need File size metrics for one DB or path.
# MAGIC 
# MAGIC * To run this notebook individually for getting File size compare metrics for a path or db , follow the below steps:
# MAGIC 
# MAGIC   * Prerequisties:
# MAGIC     * Hive metrics must be generated(using jupyter hub/Putty notebook)
# MAGIC   * Pass mount path & the Hive metrics file name in widgets (will appear at top of this notebook) after running cmd 2 , Below is Sample input:
# MAGIC     *  mount_path =>'/kh/dev/published/hive/kh_dev_published_src_ams_db' (pass the path for which you need the metrics)
# MAGIC     * hive_file_folder_count_filename => 'Hive_kh_dev_published_src_ams_db_Metadata_File_Folder_Count.csv' (pass the Hive metrics result csv file name)
# MAGIC   * To place the Hive result generated from jupyter hub/putty, Run upto cmd 4 (to create current date folder) & place the hive result in the ADLS (/wandisco/Test_Validation/Metadata/yyyyMMdd/) - (Note : If already date folder is available in ADLS with Hive result, skip this step & run the entire notebook)
# MAGIC   * once the above two are done run the entire notebook 

# COMMAND ----------

# DBTITLE 1,Input parameter are declared here
#Pass the value of Mount path & Hive File folder count Metrics result file name in widgets
dbutils.widgets.removeAll()
dbutils.widgets.text("mount_path","")
dbutils.widgets.text("hive_file_folder_count_filename","")
mount_path = dbutils.widgets.get("mount_path")
hive_file_folder_count_filename = dbutils.widgets.get("hive_file_folder_count_filename")

#mount_path = '/kh/prod/published/hive/kh_published_cas_db' 
#hive_file_folder_count_filename = 'Hive_kh_published_cas_db_Metadata_File_Folder_Count.csv'


# COMMAND ----------

# MAGIC %run ./02_Utilities

# COMMAND ----------

DateFolder = date.today().strftime("%Y%m%d")
mount_point = dbfs_mount_path + wandisco_container_name + mount_path
FileName = hive_file_folder_count_filename.split(".")[0].replace("Hive_","")
dest_path =  "/Test_Validation/Metadata/"+DateFolder+"/"
#mount path
mount_container( wandisco_container_name)
#Note :Create date folder in ALDS to place Hive result 
#New path created by below code : /mnt/wandisco/Test_Validation/Metadata/yyyyMMdd/ -> current date in yyyyMMdd format
dbutils.fs.mkdirs (dbfs_mount_path + wandisco_container_name + dest_path)
#Note: Place both File size & File folder count metrics result that was extracted after Hive - Putty scripts after the directory is created in ADLS
print(dbfs_mount_path + wandisco_container_name + dest_path)

# COMMAND ----------

#fetch the src metrics(Hive csv result) file placed in adls
sourceDF = spark.read.format("csv") \
    .option("inferSchema", "true") \
    .option("header", "true") \
    .option("sep", ",") \
    .load(dbfs_mount_path + wandisco_container_name +dest_path+hive_file_folder_count_filename)
sourceDF =sourceDF.toPandas()

# COMMAND ----------

display(sourceDF)

# COMMAND ----------

#Function to retrive file & folder count info of all the files in ADLS tgt mounted path
rddArr = []

def iterate_path(path):
    total_files = 0
    total_folders = 0
    path_list = dbutils.fs.ls(path)
    if path_list:
        for path_object in path_list:
            tempPath = path_object.path.replace(("dbfs:" + "/mnt/wandisco"), "")
            if (str(tempPath).startswith("Test_Validation") == False) and (str(tempPath).startswith("ORC_ACID_to_Parquet_Conversion") == False):
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

#Create ADLS csv metrics file & save to adls
targetDF = spark.createDataFrame(rdd, schema)
targetDF = targetDF.toPandas()
targetDF.to_csv('/dbfs' + dbfs_mount_path + wandisco_container_name + dest_path + 'ADLS_' + FileName + '.csv',header=True)

# COMMAND ----------

display(targetDF)


# COMMAND ----------

#Form the compare dataset between Hive vs ADLS
CompareDF = sourceDF.merge(targetDF, on="Path",how='outer',suffixes=['', '_tgt'], indicator=True)

#Create the Value Diff metrics after comparing src & tgt
CompareDF['FolderCountValueDiff'] = CompareDF['FolderCount'].sub(CompareDF['FolderCount_tgt'])
CompareDF['FolderCount%diff'] = percentage_change(CompareDF['FolderCount'],CompareDF['FolderCount_tgt'])
CompareDF['FileCountValueDiff'] = CompareDF['FileCount'].sub(CompareDF['FileCount_tgt'])
CompareDF['FileCount%diff'] = percentage_change(CompareDF['FileCount'],CompareDF['FileCount_tgt'])

# COMMAND ----------

display(CompareDF)

# COMMAND ----------

# Save the compare result into Test_Validation current date folder as csv file
CompareDF.to_csv('/dbfs' + dbfs_mount_path + wandisco_container_name + dest_path + 'Compare_' + FileName + '.csv',header=True)
