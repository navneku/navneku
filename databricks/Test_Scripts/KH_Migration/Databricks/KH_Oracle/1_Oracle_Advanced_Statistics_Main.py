# Databricks notebook source
# DBTITLE 1,Introduction to run this notebook
# MAGIC %md
# MAGIC This notebook runs another notebook, as per the iteration on the active tables list given in csv file AdvancedStats_Config.csv --> placed inside dev(or)prod/Test_Validation/Oracle/Advanced_Statistics/.

# COMMAND ----------

# MAGIC %run ../02_Utilities

# COMMAND ----------

# MAGIC %md
# MAGIC Next Command is one time activity to create timebased directory in the conatiner for active tables from the list.
# MAGIC * Once the directories are created, place/upload the metrics result files generated from putty/jupyterHub in the current dates directory of each active table
# MAGIC * Then only run next command cell

# COMMAND ----------

# DBTITLE 1,Create directory for each table to upload Hive Results
DateFolder = date.today().strftime("%Y%m%d")
dest_path =  "/Test_Validation/Oracle/Advanced_Statistics/"

#path in which the test scripts are placed in databricks
AdvancedStats_notebook ='1.1_Oracle_vs_ADLS_Advanced_Statistics'
#mount the dev/prod container
mount_container( test_container_name)

#Read the Oracle_AdvancedStats_Config.csv file placed at dev or prod container "/Test_Validation/Oracle/Advanced_Statistics/" and run the test script for all the active Tables listed in the config file 

#New path created: /mnt/<dev(or)prod>/Test_Validation/Oracle/AdvancedStats/yyyyMMdd/
dbutils.fs.mkdirs (dbfs_mount_path + test_container_name + dest_path + DateFolder)


#Note: 4 Upload Hive results for each active table in this directory created in ADLS

# COMMAND ----------

"/dbfs"+dbfs_mount_path + test_container_name + dest_path + OracleAdvancedStatsConfig

# COMMAND ----------

# DBTITLE 1,Runs the next notebook here for each table name (iterated)
#Read the AdvancedStats_Config.csv file placed at dev/prod container "/Test_Validation/Oracle/Advanced_Statistics/" and run the test script for all the active Tables listed in the config file 
with open("/dbfs"+dbfs_mount_path + test_container_name + dest_path + OracleAdvancedStatsConfig,"r") as read_obj:
    csv_reader = csv.reader(read_obj)
    header = next(csv_reader)
    #Check file as empty
    if header !=None:
        for row in csv_reader:
            print(row)
            if row[4]== "1":
                ContainerName = row[0]
                DBSchema = row[1]
                TableName = row[2]
                PrimaryKey = row[3]
                dbutils.notebook.run("./"+AdvancedStats_notebook,0,{
                    "ContainerName":ContainerName,
                    "DBSchema" : DBSchema,
                    "TableName" : TableName,
                    "PrimaryKey" : PrimaryKey,
                })
