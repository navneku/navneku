# Databricks notebook source
# MAGIC %run "./Databricks/02_Utilities"

# COMMAND ----------

mount_container(wandisco_container_name)

# COMMAND ----------

spark.read.format("ORC").load("/mnt/wandisco/kh/cas_dev/published/hive/kh_dev_published_src_cas_db/TAIS_IF02_XML")

# COMMAND ----------

spark.read.format("ORC").load("/mnt/wandisco/kh/ldmnonprod/published/hive/kh_dev_published_src_ams_db/TAMS_AGENTS")

# COMMAND ----------


