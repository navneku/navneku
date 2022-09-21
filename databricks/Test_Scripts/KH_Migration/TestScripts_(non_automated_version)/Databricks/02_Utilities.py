# Databricks notebook source
# MAGIC %run ./01_Initialize

# COMMAND ----------

#un mount
def unmount(mnt_path):
    dbutils.fs.unmount(mnt_path)

# COMMAND ----------

# Check if folder exist
def folder_exist(path):
    try:
        dbutils.fs.ls(path)
        return True
    except:
        return False

# COMMAND ----------

# Delete the folder and its contents
def delete_folder_files(directory_path):
    folders_batch = dbutils.fs.ls(directory_path)

    # Check if folder exist, then delete
    if folder_exist(directory_path):
        for i in range (0, len(folders_batch)):
            folder = folders_batch[i].name

            # Delete each folder
            dbutils.fs.rm(directory_path + "/" + folder, True)

        # Delete the parent folder
        dbutils.fs.rm(directory_path, True)

# COMMAND ----------

# Get all Parquet files in a directory
def get_all_files(directory_path,file_extension):
    all_files = []
    files_to_treat = dbutils.fs.ls(directory_path)
    
    while files_to_treat:
        path = files_to_treat.pop(0).path
        all_files.append(path)
        #if path.endswith("/"):
        #    files_to_treat += dbutils.fs.ls(path)
        #elif path.endswith(file_extension):
        #    all_files.append(path)
        
    return all_files

# COMMAND ----------

def recursiveDirSize(path):
    total = 0
    dir_files = dbutils.fs.ls(path)
    for file in dir_files:
        if file.isDir():
            total += recursiveDirSize(file.path)
        else:
            total = file.size
        return total

# COMMAND ----------

def run_with_retry(notebook, timeout, args = {}, max_retries = 0):
    num_retries = 0
    while True:
        try:
            return dbutils.notebook.run(notebook, timeout, args)
        except Exception as e:
            if num_retries >= max_retries:
                raise e
            else:
                print("Retrying error", e)
                num_retries += 1

# COMMAND ----------

#find size of the file
def discover_size(path: str, verbose: bool = True):
    def loop_path(paths: List[FileInfo], accum_size: float):
        if not paths:
            return accum_size
        else:
            head, tail = paths[0], paths[1:]
            if head.size > 0:
                if verbose:
                    print(f"{head.path}: {head.size / 1e6} MB")
                    accum_size += head.size / 1e6
                    return loop_path(tail, accum_size)
                else:
                    extended_tail = dbutils.fs.ls(head.path) + tail
                    return loop_path(extended_tail, accum_size)

    return loop_path(dbutils.fs.ls(path), 0.0)

# COMMAND ----------

def path_exists(path):
    try:
        if len(dbutils.fs.ls(path)) > 0:
            return True
    except:
        return False

# COMMAND ----------


def mount_adls_container(containername):
    dbutils.fs.mount(
        source = f"wasbs://{containername}@{storage_account}.blob.core.windows.net",
        mount_point  = dbfs_mount_path + containername,
        extra_configs = {f"fs.azure.account.key.{storage_account}.blob.core.windows.net":storage_secret}
    )

# COMMAND ----------

# DBTITLE 1,Schema Reading From Synapse
def synapse_table_df(tbl_name):
    #tbl_nm = schema_db+"."+tbl_name
    df = spark.read \
        .format("jdbc") \
        .option("url", url) \
        .option("dbtable", tbl_name) \
        .option("user", username) \
        .option("password", password).load()
    return df #will fetch schema from here only

# COMMAND ----------

#ADLS Processing
def check_if_mounted(mount_path):
    try:
        dbutils.fs.ls(mount_path)
        return True
    except:
        return False

def mount_container(container_name):
    mnt_path = dbfs_mount_path +container_name
    if check_if_mounted(mnt_path)!=True:
        dbutils.fs.mount(
        source = f"wasbs://{container_name}@{storage_account}.blob.core.windows.net",
        mount_point = mnt_path,
        extra_configs = {f"fs.azure.account.key.{storage_account}.blob.core.windows.net":storage_secret}
    )
def load_adls_df(file_path,file_format,file_name=None,schema=None):
    if file_format=="orc-acid":
        file_format="orc"
    path=dbfs_mount_path+container+file_path
    #print(path)
    if file_name!=None:
        if file_name!='' and file_format!='orc':
            path=file_path+'/'+file_name+'.'+file_format
            print(path)
    if file_format=="csv":
        df = spark.read.format('csv').option("header","true").load(path)
    elif file_format == "tsv":
        df = spark.read.format("csv").option("header", "false").option("sep", "\t").load(path)
    elif file_format=="parquet" or file_format=="orc":
        df = spark.read.format(file_format).load(path)

    return df



# COMMAND ----------

# DBTITLE 1,ORC Acid File Conversion
def orc_acid_conversion(pyspark_df):
    dfpanda = pyspark_df.toPandas()
    Row_list=[]
    for index, rows in dfpanda.iterrows():
        # Create list for the current row
        my_list =rows.row

        # append the list to the final list
        Row_list.append(my_list)
    df_final = spark.createDataFrame(Row_list,[])
    return df_final

# COMMAND ----------

# DBTITLE 1,ORC acid file conversion with schema provided
def orc_acid_conversion_with_schema_provided(pyspark_df,schema):
    dfpanda = pyspark_df.toPandas()
    Row_list=[]
    for index, rows in dfpanda.iterrows():
        # Create list for the current row
        my_list =rows.row

        # append the list to the final list
        Row_list.append(my_list)
    rdd = spark.sparkContext.parallelize(Row_list)
    df_final = spark.createDataFrame(rdd, schema)
    return df_final

# COMMAND ----------

#Write result
def write_spark_df(df,dest,file_format='csv'):
    df.coalesce(1).write.format(file_format).option("header","true").save(dest)
def write_pandas_df(df,dest):
    df.to_csv(dest,header="true")

# COMMAND ----------

# DBTITLE 1,Check Primary Key
def check_primary_key(df,prim_key, db_nm, tbl_nm):
    #df = synapse_table_df(tbl_name)
    
    df.createOrReplaceTempView(tbl_nm)
    
    df = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                     + "' as table_name, 'unique count' as measure, 'primary key' as column_value, count(distinct " + prim_key
                                           + ") as freq from " + tbl_nm)
    df = df.toPandas()
    
    
    df2 = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                 + "' as table_name, 'record count' as measure, '' as column_value, count(*) as freq from " + tbl_nm)
    df2 = df2.toPandas()
    
    df3 = spark.sql("describe " + tbl_nm)
    df3 = df3.toPandas()
    

    df = df.append(df2)#, ignore_index = True)
    #returning pandas dataframe
    return df.append(pd.DataFrame([[db_nm, tbl_nm, 'field count', '', len(df3)]], columns=df.columns))


# COMMAND ----------

# DBTITLE 1,Advanced Statistics All Together

def check_data_types(prim_key, db_nm, tbl_nm, df):

    
    df.createOrReplaceTempView(tbl_nm)
    
    df = spark.sql("describe " + tbl_nm)
    df = df.toPandas()
    
    df = df[(df.col_name != prim_key)]
    cat_df = df[df["data_type"].str.contains("varchar|string")] #Get only fields with categorical data types
    num_df = df[df["data_type"].str.contains("int|double|bigint|decimal")] #Get only fields with numeric data types
    date_df = df[df["data_type"].str.contains("date|timestamp")] #Get only fields with categorical data types

    # 2a. check categorical data types

    def check_string_types(db_nm, tbl_nm, cat_df):

        if len(cat_df) > 0:

            df_tmp = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "column_value", "freq"])
            df_cat = pd.DataFrame()

            for field in cat_df["col_name"]:
                
                df_tmp = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                             + "' as table_name, '" + field + "' as column_name, " + field
                                                         + " as column_value, count(*) as freq from " + tbl_nm
                                                         + " group by " + field)
                df_tmp = df_tmp.toPandas()
                
                if len(df_tmp) > 0:
                    df_cat = df_cat.append(df_tmp)
                else:
                    df_cat = df_cat.append(pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan]]))#,ignore_index = True))

        else:
            df_cat = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "column_value", "freq"])

        return df_cat


    # 2b. check numeric data types

    def check_numeric_types(db_nm, tbl_nm, num_df):

        if len(num_df) > 0:

            df_tmp = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "min", "max", "avg", "stddev", "10th_percentile", "20th_percentile", "30th_percentile", "40th_percentile", "50th_percentile", "60th_percentile", "70th_percentile", "80th_percentile", "90th_percentile", "null_values"])
            df_num = pd.DataFrame()

            for field in num_df["col_name"]:

                df_tmp = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                             + "' as table_name, '" + field + "' as column_name, min(" + field
                                                         + ") as min_value, max(" + field
                                                         + ") as max_value, avg(" + field
                                                         + ") as avg_value, stddev(" + field
                                                         + ") as stddev_value, percentile_approx(" + field
                                                         #+ ", 0.00) as 0th_percentile, percentile_approx(" + field
                                                         + ", 0.10) as 10th_percentile, percentile_approx(" + field
                                                         + ", 0.20) as 20th_percentile, percentile_approx(" + field
                                                         + ", 0.30) as 30th_percentile, percentile_approx(" + field
                                                         + ", 0.40) as 40th_percentile, percentile_approx(" + field
                                                         + ", 0.50) as 50th_percentile, percentile_approx(" + field
                                                         + ", 0.60) as 60th_percentile, percentile_approx(" + field
                                                         + ", 0.70) as 70th_percentile, percentile_approx(" + field
                                                         + ", 0.80) as 80th_percentile, percentile_approx(" + field
                                                         + ", 0.90) as 90th_percentile, sum(case when " + field
                                                         + " is null then 1 else 0 end) as null_values from " + tbl_nm)
                df_tmp = df_tmp.toPandas()
                
                if len(df_tmp) > 0:
                    df_num = df_num.append(df_tmp)
                else:
                    df_num = df_num.append(pd.DataFrame([[field, np.nan, np.nan, np.nan, np.nan, np.nan,
                    np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]]))#,ignore_index = True))

            df_num_unpivot = pd.melt(df_num, id_vars = ['schema_name', 'table_name', 'column_name'])

        else:
            df_num_unpivot = pd.DataFrame(columns=["schema_name", "table_name", "column_name", "column_value", "freq"])

        return df_num_unpivot



    # 2c. check date data types

    def check_date_types(db_nm, tbl_nm, date_df):

        if len(date_df) > 0:

            df_tmp = pd.DataFrame(columns=["schema_name", "table_name", "column_name", 'date_type', "column_value", "freq"])
            df_date = pd.DataFrame()
            date_components = ["year", "month", "day"]
            measures = ["max", "min"]

            for field in date_df["col_name"]:
                for metric in date_components:

                    df_tmp = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                             + "' as table_name, '" + field + "' as column_name, '" + metric + "' as date_type, " + metric + "(" + field
                                                             + ") as column_value, count(*) as freq from " + tbl_nm
                                                             + " group by " + metric + "(" + field + ")")
                    df_tmp = df_tmp.toPandas()

                    if len(df_tmp) > 0:
                        df_date = df_date.append(df_tmp)
                    else:
                        df_date = df_date.append(pd.DataFrame([[field, np.nan, np.nan, np.nan, np.nan, np.nan]]))#,ignore_index = True))

            for field in date_df["col_name"]:
                for metric in measures:

                    df_tmp = spark.sql("select '" + db_nm + "' as schema_name ,'" + tbl_nm
                             + "' as table_name, '" + field + "' as column_name, " + "'boundary' as date_type, '" + metric + "imum' as column_value, "
                                                            + metric + "(" + field + ") as freq from " + tbl_nm)
                    df_tmp = df_tmp.toPandas()

                    if len(df_tmp) > 0:
                        df_date = df_date.append(df_tmp)
                    else:
                        df_date = df_date.append(pd.DataFrame([[field, np.nan, np.nan, np.nan, np.nan, np.nan]]))#,ignore_index = True))

        else:
            df_date = pd.DataFrame(columns=["schema_name", "table_name", "column_name", 'date_type', "column_value", "freq"])

        return df_date

    return check_string_types(db_nm, tbl_nm, cat_df), check_numeric_types(db_nm, tbl_nm, num_df), check_date_types(db_nm, tbl_nm, date_df)

# COMMAND ----------

# DBTITLE 1,Percentage Metrics
def percentage_change(col1,col2):
    return ((col2 - col1) / col1) * 100
