# Databricks notebook source
# DBTITLE 0,Script For Automation
#Generates Hive side File Folder Count metrics - Databricks notebook source
import subprocess
import os
import csv
with open("Metadata_Config.csv","r") as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        #Check file as empty
        if header !=None:
                for row in csv_reader:
                        #print(row[0])
                        if row[2] == '1':
                                kerberos_keytab = "/etc/security/keytabs/sqoop.headless.keytab"
                                host_name = "sqoop@P01EAEDL.MANULIFE.COM"
                                kerberos_list = ["kinit","-kt",kerberos_keytab,host_name]
                                kb_run = subprocess.Popen(kerberos_list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                                mnt_path = row[0]
                                args_list = ['hdfs', 'dfs', '-ls', '-R', mnt_path]
                                proc = subprocess.Popen( args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                r_f = 0
                                r_file = 0
                                dict_by_loc={}
                                l =[]
                                mnt_pt= mnt_path.split('/',1)[1]
                                for path in iter(proc.stdout.readline, ""):
                                        fo = path.split('/',1)[1].replace(mnt_pt+"/","").replace("\n","")
                                        if path[0]=='d' and ('.hive' not in path):
                                                #print(path.split(" ")[-1].replace(mnt_path+"/",""),path[0:4])
                                                d={"Path":mnt_path+"/"+fo+"/","FolderCount":0,"FileCount":0}
                                                dict_by_loc[fo+"/"]=d
                                        temp = fo.rsplit("/",1)
                                        if(len(temp)==1):
                                                if(path[0]=='d' and ('.hive' not in path)):
                                                        r_f+=1
                                                elif(path[0]!='d' and ('.hive' not in path)):
                                                        r_file+=1
                                        else:
                                                #print(temp[0]+"/")
                                                if(path[0]=='d' and ('.hive' not in path)):
                                                        dict_by_loc.get(temp[0]+"/")["FolderCount"]+=1
                                                elif (path[0]!='d' and ('.hive' not in path)):
                                                        dict_by_loc.get(temp[0]+"/")["FileCount"]+=1
                                l = dict_by_loc.values()
                                l.append({"Path":mnt_path +"/","FolderCount":r_f,"FileCount":r_file})
                                cols = ["Path","FolderCount","FileCount"]
                                csv_file = "Hive_"+row[1]+"_Metadata_File_Folder_Count.csv"
                                try:
                                        with open(csv_file,'w') as csvfile:
                                                writer = csv.DictWriter(csvfile,fieldnames=cols)
                                                writer.writeheader()
                                                for data in l:
                                                        writer.writerow(data)
                                except IOError:
                                        print("I/O error")
