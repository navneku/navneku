# Databricks notebook source
# DBTITLE 1,Introduction & How to Run this notebook
# MAGIC %md
# MAGIC This notebook (Test script) generates ADLS metrics like the File sizes & file folder count for all paths in Metadata_Config.csv file with ActiveFlag as '1' & compares them between HDFS Vs ADLS
# MAGIC * Prerequisties:
# MAGIC   * Hive metrics must be generated(using jupyter hub/Putty notebook)
# MAGIC   * Metadata_Config.csv file in Wandisco Container "/Test_Validation/Metadata/" folder must be updated with the list of DB for with the test scripts has to be executed
# MAGIC   * Note: This notebook will run for all the entry in Metadata_Config.csv file with ActiveFlag = '1' -> Update ActiveFlag in this file accordingly (based on which DB metrics you need)
# MAGIC * Run upto cmd 3 to create date folder in ADLS to place the Hive result & place the result that was generated from Putty/jupyterhub
# MAGIC * Once above step is completed run the entire notebook to generate file size & file folder count ADLS & compare metrics
# MAGIC 
# MAGIC * Note: Please make sure the Hive result file names are in the below format:
# MAGIC   * Hive_File_Size : Hive_(DBName)_Metadata_File_Size.csv
# MAGIC   * Hive_File_Folder_Count :  Hive_(DBName)_Metadata_File_Folder_Count.csv (DBName from Metadata_Config.csv file)

# COMMAND ----------

# MAGIC %run ./02_Utilities

# COMMAND ----------

# DBTITLE 1,Create Date folder in ADLS to place Hive metrics(Read the Notes provided)
DateFolder = date.today().strftime("%Y%m%d")
dest_path =  "/Test_Validation/Metadata/"+DateFolder+"/"
Config_filepath= "/Test_Validation/Metadata/"

#path in which the test scripts are placed in databricks
File_Size_notebook ='3.1.1_Hive_vs_ADLS_Metadata_File_Size'
File_Folder_Count_notebook ='3.1.2_Hive_vs_ADLS_Metadata_File_Folder_Count'

#mount the wandisco container
mount_container( wandisco_container_name)
#Note: New path created by below code : /mnt/wandisco/Test_Validation/Metadata/yyyyMMdd/ -> current date in yyyyMMdd format
dbutils.fs.mkdirs (dbfs_mount_path + wandisco_container_name + dest_path)
print(dbfs_mount_path + wandisco_container_name + dest_path)

#Note: Place both File size & File folder count metrics result that was extracted after Hive - Putty scripts after the directory is created in ADLS

# COMMAND ----------

# DBTITLE 1,To generate File Size  ADLS metrics & compare Metrics
#Read the Metadata_Config.csv file placed at wandisco container "/Test_Validation/Metadata/" and run the test script for all the DB in the config file to generate File_Size metrics
with open("/dbfs"+dbfs_mount_path + wandisco_container_name + Config_filepath + MetadataConfig,"r") as read_obj:
    csv_reader = csv.reader(read_obj)
    header = next(csv_reader)
    #Check file as empty
    if header !=None:
        for row in csv_reader:
            if row[2]== "1":
                hive_file_size_filename= "Hive_" + row[1] +"_Metadata_File_Size.csv"
                dbutils.notebook.run("./" + File_Size_notebook,0,
                {
                 "mount_path": row[0],
                 "hive_file_size_filename": hive_file_size_filename
                })

# COMMAND ----------

# DBTITLE 1,To generate File Folder Count  ADLS metrics & compare Metrics
#Read the Metadata_Config.csv file placed at wandisco container "/Test_Validation/Metadata/" and run the test script for all the DB in the config file to generate File Folder Count metrics
with open("/dbfs"+dbfs_mount_path + wandisco_container_name + Config_filepath + MetadataConfig,"r") as read_obj:
    csv_reader = csv.reader(read_obj)
    header = next(csv_reader)
    #Check file as empty
    if header !=None:
        for row in csv_reader:
            if row[2]== "1":
                hive_file_folder_count_filename= "Hive_" + row[1] +"_Metadata_File_Folder_Count.csv"
                dbutils.notebook.run("./" + File_Folder_Count_notebook,0,
                {
                 "mount_path": row[0],
                 "hive_file_folder_count_filename": hive_file_folder_count_filename
                })
