# File Imports
import json
import time
from math import floor
import os
from subprocess import check_call
# Minio Imports
from minio import Minio
import os


def makeFileName(prefix,msgBlockStart,postfix):
    if prefix is None:
        return str(floor(msgBlockStart))+postfix
    else:
        return prefix + '_' + str(floor(msgBlockStart)) + postfix

class toFile():
    def __init__(self,fdOut,prefix,compress=True,deletetmpfile=True): 
            msgBlockStart=time.time()
            self.filepath=os.path.join(fdOut,makeFileName(prefix,msgBlockStart,'.njson'))
            self.fout=open(self.filepath,'w')   
            self.compress=compress
            self.deletetmpfile=deletetmpfile

    def close(self):
        self.fout.close()
        if self.compress:
            print('Compressing file')
            check_call(['gzip', self.filepath])
            self.filepath=self.filepath+'.gz'
    
    def cleanup(self):
        rm_file=self.filepath
        if self.deletetmpfile:
            print('Deleting local tmp files')
            check_call(['rm', rm_file])            

    # def delzip(self):
    #     rm_file=self.filepath
    #     print('Deleting zip file')
    #     check_call(['rm', rm_file])      

            
    def proc(self,message):
        self.fout.write(json.dumps(dict({'properties':message.properties,'body':message.body}))+'\n')
        

def toS3(s3conn_options,bucket_options,filepath):
    s3conn=Minio(**s3conn_options)
    bucketfound = s3conn.bucket_exists(bucket_options['bucket_name'])
    if not bucketfound and bucket_options['make_bucket']:
        s3conn.make_bucket(bucket_options['bucket_name'])
    pathfd, filename = os.path.split(filepath)
    s3conn.fput_object(bucket_options['bucket_name'], filename, filepath)
    print('Upload to bucket')
