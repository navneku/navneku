# Databricks notebook source
import subprocess
import os
import csv
mnt_path="/kh/cas_dev/processing/hive/kh_dev_processing_src_cas_db"

#args_list = ['hdfs', 'dfs', '-ls', '-R', mnt_path]
args_list = ['hadoop', 'fs', '-ls', '-R', mnt_path]
proc = subprocess.Popen( args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
r_f = 0
r_file = 0
dict_by_loc={}
#l =[]
#global dict_by_loc
for path in iter(proc.stdout.readline, ""):
        path = str(path).replace("\\n'","").replace("b'","")
        if(len(path))>3:
                fo = path.split(" ")[-1].replace(mnt_path+"/","")
                print(path)
                if path[0]=='d':
                        #print(path.split(" ")[-1].replace(mnt_path+"/",""),path[0:4])
                        d={"Path":fo+"/","FolderCount":0,"FileCount":0}
                        print(fo+"/",fo)
                        dict_by_loc[fo+"/"]=d
                temp = fo.rsplit("/",1)
                if(len(temp)==1):
                        if(path[0]=='d'):
                                r_f+=1
                        else:
                                r_file+=1
                else:
                        print(temp[0]+"/")
                        if(path[0]=='d'):
                                dict_by_loc.get(temp[0]+"/")["FolderCount"]+=1
                        else:
                                dict_by_loc.get(temp[0]+"/")["FileCount"]+=1
        else:
            break
#l = dict_by_loc.values()
#l.append({"Path":"/","FolderCount":r_f,"FileCount":r_file})

cols = ["Path","FolderCount","FileCount"]
csv_file = "Hive_"+mnt_path.split("/")[-1]+"_Metadata_File_Folder_Count.csv"
try:
        with open(csv_file,'w') as csvfile:
                writer = csv.DictWriter(csvfile,fieldnames=cols)
                writer.writeheader()
                #for data in l:
                #        writer.writerow(data)
                for data,value in dict_by_loc.items():
                        writer.writerow(value)
                writer.writerow({"Path":"/","FolderCount":r_f,"FileCount":r_file})
except IOError:
        print("I/O error")
