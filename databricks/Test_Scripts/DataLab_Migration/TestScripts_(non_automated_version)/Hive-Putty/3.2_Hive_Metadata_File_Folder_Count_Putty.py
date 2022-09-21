# Databricks notebook source
#Generates Hive side metrics - Databricks notebook source
import subprocess
import os
import csv
kerberos_keytab = "/etc/security/keytabs/sqoop-d02saedl.keytab"
host_name = "sqoop-d02saedl@P01EAEDL.MANULIFE.COM"
kerberos_list = ["kinit","-kt",kerberos_keytab,host_name]
kb_run = subprocess.Popen(kerberos_list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
mnt_path=raw_input("Enter mount path(e.g. /kh/dev/published) :")
args_list = ['hdfs', 'dfs', '-ls', '-R', mnt_path]
#args_list = ['hdoop', 'fs', '-du', '-h', mnt_path]
proc = subprocess.Popen( args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
r_f = 0
r_file = 0
dict_by_loc={}
l =[]
#global dict_by_loc
for path in iter(proc.stdout.readline, ""):
        #if(len(path))>3:
        fo = path.split(" ")[-1].replace(mnt_path+"/","").replace("\n","")
        if path[0]=='d':
                #print(path.split(" ")[-1].replace(mnt_path+"/",""),path[0:4])
                d={"Path":mnt_path+"/"+fo+"/","FolderCount":0,"FileCount":0}
                dict_by_loc[fo+"/"]=d
        temp = fo.rsplit("/",1)
        if(len(temp)==1):
                if(path[0]=='d'):
                        r_f+=1
                else:
                        r_file+=1
        else:
                #print(temp[0]+"/")
                if(path[0]=='d'):
                        dict_by_loc.get(temp[0]+"/")["FolderCount"]+=1
                else:
                        dict_by_loc.get(temp[0]+"/")["FileCount"]+=1
l = dict_by_loc.values()
l.append({"Path":mnt_path +"/","FolderCount":r_f,"FileCount":r_file})
cols = ["Path","FolderCount","FileCount"]
if mnt_path.split("/")[-1] == 'hive':
    csv_file = "Hive_"+mnt_path.split("/")[-2]+"_Metadata_File_Folder_Count.csv"
else:
    csv_file = "Hive_"+mnt_path.split("/")[-1]+"_Metadata_File_Folder_Count.csv"
try:
        with open(csv_file,'w') as csvfile:
                writer = csv.DictWriter(csvfile,fieldnames=cols)
                writer.writeheader()
                for data in l:
                        writer.writerow(data)
except IOError:
        print("I/O error")
