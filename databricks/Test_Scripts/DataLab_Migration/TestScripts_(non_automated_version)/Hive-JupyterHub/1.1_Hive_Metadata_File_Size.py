# Databricks notebook source
import subprocess
import os
import csv
mnt_path="/kh/cas_dev/processing/hive/kh_dev_processing_src_cas_db/CAS_TCLIENT_ADDRESSES"
args_list = ['hadoop', 'fs', '-ls', '-R', mnt_path]
#args_list = ['hdfs', 'dfs', '-du', '-h', mnt_path]
proc = subprocess.Popen( args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
csv_file = "Hive_"+mnt_path.split("/")[-1]+"_Metadata_File_Size.csv"
cols =['FilePath','FileName','Size(Bytes)','FileType']
mat=[]
for path in iter(proc.stdout.readline, ""):
    path = str(path)#.replace("b'","")
    print(path)
    if len(path)>3 and path.startswith('d')==False:
        #print(path)      
        l = path.split(" ")
        #print(l[-1].replace(mnt_path,""),l[-4],l[-3])
        fname = l[-1].replace(mnt_path,"").strip().split("/")[-1]
        ans=[l[-1].replace("\\n'","").strip(),fname.replace("\\n'",""),l[-4].replace("\\n'",""),fname.split(".")[-1].replace(fname,"orc")]
        mat.append(ans)
    else:
        break


print(mat[0])
with open(csv_file,'w') as f:
    write = csv.writer(f)
    write.writerow(cols)
    write.writerows(mat)
