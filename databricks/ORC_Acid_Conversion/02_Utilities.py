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

def path_exists(path):
    try:
        if len(dbutils.fs.ls(path)) > 0:
            return True
    except:
        return False

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
    elif file_format=="parquet" or file_format=="orc":
        df = spark.read.format(file_format).load(path)

    return df



# COMMAND ----------

rddArr = []
def get_orc_acid_file_path(path,container):
    #accum_size = 0
    path_list = dbutils.fs.ls(path)
    if path_list:
        for path_object in path_list:
            tempPath = path_object.path.replace(("dbfs:" + "/mnt/"+container), "") 
            if path_object.path[-1] != '/' and str(path_object.path).endswith("_orc_acid_version"):
                #accum_size += path_object.size 
                rddArr.append(("/mnt/"+container+tempPath.replace(path_object.name,''), path_object.name))            
            else:
                if(path_object.path[-1] == '/'):
                    get_orc_acid_file_path(path_object.path,container)
    

# COMMAND ----------

def get_dir_content(ls_path):
    dir_paths = dbutils.fs.ls(ls_path)
    subdir_paths = [get_dir_content(p.path) for p in dir_paths if p.isDir() and p.path != ls_path]
    flat_subdir_paths = [p for subdir in subdir_paths for p in subdir]
    return list(map(lambda p: p.path, dir_paths)) + flat_subdir_paths
