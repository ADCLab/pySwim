from __future__ import print_function
from proton.reactor import Container
from proton.handlers import MessagingHandler
import time
from loadenv import Options
from wrtr import toFile, toS3, makeFileName
import sys
import json
from io import StringIO  # Python 3.x
import gzip
from math import ceil


class Recvr(MessagingHandler):
    def __init__(self, opts):
        super(Recvr, self).__init__()
        # TIMING SETTINGS
        self.startTime=time.time()
        self.opts=opts
        self.messages=[]        
        
    def on_reactor_init(self, event):  
        self.container = event.reactor
        self.container.schedule(self.opts.runtime, self)
        conn = event.container.connect(url=self.opts.amqp_connection_url, 
                                       user=self.opts.connection_username, 
                                       password=self.opts.connection_password, 
                                       allow_insecure_mechs=True)
        if conn:
            event.container.create_receiver(conn, source=self.opts.queue_name)
            print('Connection Establish')

    def on_timer_task(self, event):
        event.container.stop()        
        print('Connection Terminated')
        if self.opts.output_maxsize==0:
            messageChunks=['\n'.join(self.messages)]
            numChunks=['']
        else:
            totalSizeInMB=sum([sys.getsizeof(message) for message in self.messages])/1024/1024
            numberOfFiles=ceil(totalSizeInMB/self.opts.output_maxsize)
            numberOfMessagesPerFile=ceil(len(self.messages)/numberOfFiles)
            messageChunks = ['\n'.join(self.messages[idx:idx + numberOfMessagesPerFile]) for idx in range(0, len(self.messages), numberOfMessagesPerFile)]
            numChunks=['_part%02d'%x for x in range(len(messageChunks))]
            
        for messageChunk, numChunk in zip(messageChunks,numChunks):
            filename=makeFileName(self.opts.output_prefix,self.startTime,numChunk+'.njson')
            if 'file' in self.opts.output_method:
                filepath=toFile(messages=messageChunk,
                       fdOut=self.opts.output_file_folder,
                       filename=filename,
                       compress=self.opts.output_compress)
                messageChunk=None
            else:
                filepath=None
    
    
            if 's3' in self.opts.output_method:
                s3conn_options={'endpoint':'%s:%d'%(self.opts.output_s3_host,self.opts.output_s3_port),
                           'access_key': self.opts.output_s3_access_key,
                           'secret_key': self.opts.output_s3_secret_key,
                           'secure': self.opts.output_s3_secure}
                if self.opts.output_s3_region not in [None,'']:
                    s3conn_options['region']=self.opts.output_s3_region

                bucket_options={'bucket_name':self.opts.output_s3_bucket_name,'make_bucket':self.opts.output_s3_make_bucket}
                toS3(s3conn_options=s3conn_options,
                     bucket_options=bucket_options,
                     filename=filename,
                     messages=messageChunk,
                     filepath=filepath,
                     compress=self.opts.output_compress)

    def on_message(self, event):
        self.messages.append(json.dumps(dict({'properties':event.message.properties,'body':event.message.body})))

    # the on_transport_error event catches socket and authentication failures
    def on_transport_error(self, event):
        print("Transport error:", event.transport.condition)
        MessagingHandler.on_transport_error(self, event)

    def on_disconnected(self, event):
        print("Disconnected")

def main(SWIMconfigPath='my_configVars.cfg'):
    opts = Options(SWIMconfigPath)  
    try:
        container = Container(Recvr(opts))
        container.run()
    except KeyboardInterrupt:
        container.stop()
        print()
    container.stop()

if __name__ == "__main__":
    if len(sys.argv)==1:
        main()
    else:
        main(sys.argv[1])





    