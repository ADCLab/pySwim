from __future__ import print_function
from proton.reactor import Container
from proton.handlers import MessagingHandler
import time
from loadenv import Options
from wrtr import toFile, toS3


class Recvr(MessagingHandler):
    def __init__(self, opts):
        super(Recvr, self).__init__()
        # TIMING SETTINGS
        self.startTime=time.time()
        self.opts=opts        

    def on_reactor_init(self, event):  
        self.fileout=toFile(fdOut=self.opts.output_file_folder,
                            prefix=self.opts.output_prefix,
                            compress=self.opts.output_compress,
                            deletetmpfile='file' not in self.opts.output_method)

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
        self.fileout.close()
        event.container.stop()        
        print('Connection Terminated')
        s3conn_options={'endpoint':'%s:%d'%(self.opts.output_s3_host,self.opts.output_s3_port),
                   'access_key': self.opts.output_s3_access_key,
                   'secret_key': self.opts.output_s3_secret_key,
                   'secure': self.opts.output_s3_secure}
        if self.opts.output_s3_region not in [None,'']:
            s3conn_options['region']=self.opts.output_s3_region
        else:
            print('no region')
        bucket_options={'bucket_name':self.opts.output_s3_bucket_name,'make_bucket':self.opts.output_s3_make_bucket}
    
        toS3(s3conn_options,bucket_options,self.fileout.filepath)
        self.fileout.cleanup()

    def on_message(self, event):
        self.fileout.proc(event.message)

    # the on_transport_error event catches socket and authentication failures
    def on_transport_error(self, event):
        print("Transport error:", event.transport.condition)
        MessagingHandler.on_transport_error(self, event)

    def on_disconnected(self, event):
        print("Disconnected")

# Uncomment line below if running script directly.
# opts = Options(configFile='conVars.cfg')
opts = Options()

try:
    container = Container(Recvr(opts))
    container.run()
except KeyboardInterrupt:
    container.stop()
    print()
container.stop()



    