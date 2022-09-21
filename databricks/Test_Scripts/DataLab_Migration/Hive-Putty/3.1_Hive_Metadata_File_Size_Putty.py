# Databricks notebook source
# DBTITLE 0,Script For Automation
#Generates Hive side File Size metrics - Databricks notebook source
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
                                csv_file = "Hive_"+row[1]+"_Metadata_File_Size.csv"
                                args_list = ['hdfs', 'dfs', '-ls', '-R', mnt_path]
                                proc = subprocess.Popen( args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                cols =['FilePath','FileName','Size(Bytes)','FileType']
                                mat=[]
                                for path in iter(proc.stdout.readline, ""):
                                        if path.startswith('d')==False and ('.hive' not in path):
                                                l = path.split('/',1)[0].split(" ")
                                                fname = path.rsplit('/',1)[1].strip()
                                                ans=[l[-1].strip()+'/'+fname,fname,l[-4],fname.split(".")[-1].replace(fname,"orc")]
                                                mat.append(ans)
                                #print(mat[0])
                                try:
                                    with open(csv_file,'w') as f:
                                        write = csv.writer(f)
                                        write.writerow(cols)
                                        write.writerows(mat)
                                except IOError:
                                        print("I/O error")

