import os
import configparser
from datetime import datetime

def recast(varIn,varType=str,defaultVal=None,forcelower=False):
    if varIn in [None,'']:
        if defaultVal is not None:
            return defaultVal
        else:
            return None
    elif varType==str:
        if forcelower is True:
            return str(varIn).lower().strip()
        else:
            return str(varIn).strip()

    elif varType==int:
        return int(varIn)
    elif varType==bool:
        return varIn.lower().strip() in ['true', '1']
    else:
        return None





class Options(object):    
    def __init__(self,configFile=None):
        optDict={'amqp_connection_url':(str,None),
              'queue_name':(str,None),
              'connection_username':(str,None),
              'connection_password':(str,None),
              'runtime':(int,60),
              
              'output_method':(str,'file'),
              'output_prefix':(str,None),
              'output_compress':(bool,True),
              
              'output_file_folder':(str,'/data'),
              
              'output_s3_host':(str,'127.0.0.1'),
              'output_s3_port':(int,9000),
              'output_s3_access_key':(str,None),
              'output_s3_secret_key':(str,None),
              'output_s3_bucket_name':(str,None),        
              'output_s3_make_bucket':(bool,False),        
              'output_s3_secure':(bool,False),        
              'output_s3_region':(str,None),        
            }
        
        
        if configFile is not None:
            config = configparser.ConfigParser()
            config.read(configFile)
            opt=config['options']    
            
        for cKey in optDict.keys():
            if configFile is None:
                nVal=os.environ.get(cKey.upper())
            else:
                if cKey in opt.keys():
                    nVal=opt[cKey]
                else:
                    nVal=None

            if cKey=='output_method':
                nVals=nVal.split(',')
                nValCast=[recast(varIn=nVal,varType=optDict[cKey][0],defaultVal=optDict[cKey][1],forcelower=True) for nVal in nVals]
            else:
                nValCast=recast(varIn=nVal,varType=optDict[cKey][0],defaultVal=optDict[cKey][1])
            setattr(self, cKey, nValCast)
        self.runtime=self.runtime*60
        if '<' in self.output_s3_bucket_name:
            base_path,dateformat=self.output_s3_bucket_name.split('<')
            dateformat=dateformat.split('>')[0]
            if 'yyyy' in dateformat:
                dateformat=dateformat.replace('yyyy','%Y')
            if 'yy' in dateformat:
                dateformat=dateformat.replace('yy','%y')
            if 'mm' in dateformat:
                dateformat=dateformat.replace('mm','%m')
            if 'dd' in dateformat:
                dateformat=dateformat.replace('dd','%d')
            now = datetime.now()
            self.output_s3_bucket_name=base_path +'-'+now.strftime(dateformat)
            
        
        
        
    