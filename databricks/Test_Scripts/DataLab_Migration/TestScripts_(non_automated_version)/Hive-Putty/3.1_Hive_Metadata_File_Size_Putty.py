# Databricks notebook source
#Generates Hive side metrics - Databricks notebook source
import subprocess
import os
import csv
kerberos_keytab = "/etc/security/keytabs/sqoop-d02saedl.keytab"
host_name = "sqoop-d02saedl@P01EAEDL.MANULIFE.COM"
kerberos_list = ["kinit","-kt",kerberos_keytab,host_name]
kb_run = subprocess.Popen(kerberos_list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
mnt_path=str(raw_input("Please Enter path(e.g. /kh/dev/published/hive) : "))
#"/kh/dev/published/hive"
if mnt_path.split("/")[-1] == 'hive':
    csv_file = "Hive_"+mnt_path.split("/")[-2]+"_Metadata_File_Size.csv"
else:
    csv_file = "Hive_"+mnt_path.split("/")[-1]+"_Metadata_File_Size.csv"
args_list = ['hdfs', 'dfs', '-ls', '-R', mnt_path]
#args_list = ['hdfs', 'dfs', '-du', '-h', mnt_path]
proc = subprocess.Popen( args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
cols =['FilePath','FileName','Size(Bytes)','FileType']
mat=[]
for path in iter(proc.stdout.readline, ""):
        if path.startswith('d')==False:
                l = path.split(" ")
                fname = l[-1].replace(mnt_path,"").strip().split("/")[-1]
                ans=[l[-1].strip(),fname,l[-4],fname.split(".")[-1].replace(fname,"orc")]
                mat.append(ans)               
#print(mat[0])
try:
    with open(csv_file,'w') as f:
        write = csv.writer(f)
        write.writerow(cols)
        write.writerows(mat)
except IOError:
        print("I/O error")
