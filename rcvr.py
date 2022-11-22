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



class Recvr(MessagingHandler):
    def __init__(self, opts):
        super(Recvr, self).__init__()
        # TIMING SETTINGS
        self.startTime=time.time()
        self.opts=opts
        self.messages=[]        
        self.filename=makeFileName(self.opts.output_prefix,self.startTime,'.njson')
        
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
        self.messages='\n'.join(self.messages)
        
        if 'file' in self.opts.output_method:
            filepath=toFile(messages=self.messages,
                   fdOut=self.opts.output_file_folder,
                   filename=self.filename,
                   compress=self.opts.output_compress)
            self.messages=None
        else:
            filepath=None


        if 's3' in self.opts.output_method:
            s3conn_options={'endpoint':'%s:%d'%(self.opts.output_s3_host,self.opts.output_s3_port),
                       'access_key': self.opts.output_s3_access_key,
                       'secret_key': self.opts.output_s3_secret_key,
                       'secure': self.opts.output_s3_secure}
            if self.opts.output_s3_region not in [None,'']:
                s3conn_options['region']=self.opts.output_s3_region
            else:
                print('no region')
            bucket_options={'bucket_name':self.opts.output_s3_bucket_name,'make_bucket':self.opts.output_s3_make_bucket}
            toS3(s3conn_options=s3conn_options,
                 bucket_options=bucket_options,
                 filename=self.filename,
                 messages=self.messages,
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





    