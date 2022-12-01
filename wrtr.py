# File Imports
import json
import time
from math import floor
import os
from subprocess import check_call
import gzip
from io import BytesIO
from io import StringIO

# Minio Imports
from minio import Minio
import os


def makeFileName(prefix,msgBlockStart,postfix):        
    if prefix is None:
        return str(floor(msgBlockStart))+postfix
    else:
        return prefix + '_' + str(floor(msgBlockStart)) + postfix
    
def toFile(messages, fdOut, filename, compress):
    filepath=os.path.join(fdOut,filename)
    if compress:
        filepath=filepath+'.gz'
        with gzip.open(filepath, 'wb') as f:
            f.write(messages.encode())
    else:
        with open(filepath, 'w') as f:
            f.write(messages)   
    return filepath

def toS3(s3conn_options,bucket_options,filename,messages,filepath,compress):
    s3conn=Minio(**s3conn_options)
    bucketfound = s3conn.bucket_exists(bucket_options['bucket_name'])
    if not bucketfound and bucket_options['make_bucket']:
        s3conn.make_bucket(bucket_options['bucket_name'])
    if filepath is None:
        if compress:
            filename=filename+'.gz'
            outStrIO = BytesIO()
            with gzip.GzipFile(fileobj=outStrIO, mode="w") as f:
                f.write(messages.encode())
            outStrIO.seek(0)
            s3conn.put_object(bucket_options['bucket_name'], filename, outStrIO,length=outStrIO.getbuffer().nbytes)
        else:
            outStrIO = StringIO()
            s3conn.put_object(bucket_options['bucket_name'], filename, BytesIO(messages.encode()),length=len(messages))
    else:
        pathfd, filename = os.path.split(filepath)
        s3conn.fput_object(bucket_options['bucket_name'], filename, filepath)      
    print('Upload to bucket')
