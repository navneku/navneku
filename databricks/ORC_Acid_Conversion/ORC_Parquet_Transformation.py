# Databricks notebook source
# MAGIC %run ./02_Utilities

# COMMAND ----------

container = 'wandisco'
tgt_container = 'dev'
file_format = 'orc'
#add all the tbl paths here (comma separated values)
File_path_list =['/kh/dev/published/hive/kh_dev_published_src_cas_db/Test_Table']

mount_container(container)
mount_container(tgt_container)
mnt_path = dbfs_mount_path+container
tgt_mnt_path = dbfs_mount_path+tgt_container

# COMMAND ----------

for file_path in File_path_list:
    df = load_adls_df(file_path,file_format)
    df.write.mode("overwrite").parquet(f"/mnt/{tgt_container}/parquet_file{file_path}")

# COMMAND ----------

dbutils.fs.ls(f"/mnt/{tgt_container}/parquet_file{file_path}")
