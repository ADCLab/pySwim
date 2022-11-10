# pySWIM
This small software package can be used to listen, capture, and store FAA SWIM data, either to file or to an S3 bucket.  As implemented, the package does not perform any additional filtering or processing of the data, however, you are welcome and encouraged to adjust this code to your needs.  Much of the code provided here is based on the following github repo: https://github.com/SolaceSamples/solace-samples-amqp-qpid-proton-python/blob/master/README.md  

## Requirements & Deployment
Requirements of this package depend on deployment: (1) standard execution as a script; or (2) execution within a docker container.

### Standard execution
This SWIM listener is tested to run on Ubuntu; it is doubtful the code will run in Windows or MacOS.  To execute in Ubuntu a number of packages are required for the underlying AMPQ pub/sub python module to install in your local python environment.  Install the required packages using the command below.

> sudo apt-get install -y cron gcc g++ cmake cmake-curses-gui uuid-dev libssl-dev python3-dev swig pkg-config

After installing the dependencies above the AMPQ module python-qpid-proton (https://qpid.apache.org/proton/) can be installed in your local python environment using pip.

> pip uninstall python-qpid-proton 

From there, edit the file configVars.cfg to adjust relavent paramters.  The file must begin with "[options]"; do not remove this text.  Only the required variables must be set.  All others configuration variables are optional and can be left blank or removed.  See below for additional information regarding the variables.  When using the standard execution, the configuration variable OUTPUT_FILE_FOLDER must be set (can use absolute or relative paths).

To run the SWIM listener, simply execute rcvr.py after adjusting the configuration settings.  

### Docker deployment
Docker deployment is rather straightforward (especially with Portainer, https://www.portainer.io/); as such it is the recommended means for deployment.  

Follow the standard Docker install instructions (https://docs.docker.com/engine/install/ubuntu/).  You can add your user to the docker group (https://docs.docker.com/engine/install/linux-postinstall/) so you are not required to use sudo.

The docker build is based on the python:3.8 linux image (https://hub.docker.com/_/python).  The dockerfile build steps will install all neccessary system-level packages and python packages.

In the parent directory (where this README.md file is located) build the docker image using the following command.  
> docker build -t pyswim-img -f docker/Dockerfile .
  
Replace "pyswim-img" with if you prefer a different name for the image, e.g. > docker build -t pyswim-img -f docker/Dockerfile .

To deploy and run the container you will be required to provide a number of environmental variables.  A complete list of the environmental variables are provided below.  See Docker/envVar_example for an example file.

AMQP_CONNECTION_URL=\<required\> [string] <br/>
QUEUE_NAME=\<required\> [string] <br/>
CONNECTION_USERNAME=\<required\> [string] <br/>
CONNECTION_PASSWORD=\<required\> [string] <br/>
RUNTIME=\<required\> [int :: number of minutes] <br/>
OUTPUT_METHOD=<\optional\> [str :: file, s3, or both.] <br/>
OUTPUT_PREFIX=<\optional\> [string] <br/>
OUTPUT_COMPRESS=<\optional\> [boolean] <br/>
OUTPUT_S3_HOST=\<optional\> [string :: IP address] <br/>
OUTPUT_S3_PORT=\<optional\> [int :: port] <br/>
OUTPUT_S3_ACCESS_KEY=\<optional\> [string :: s3 username] <br/>
OUTPUT_S3_SECRET_KEY=\<optional\> [string :: s3 password] <br/>
OUTPUT_S3_BUCKET_NAME=\<optional\> [string :: SEE NOTE BELOW] <br/>
OUTPUT_S3_MAKE_BUCKET=<\optional\> [boolean] <br/>
OUTPUT_S3_SECURE=<\optional\> [boolean :: SEE NOTE BELOW] <br/>
OUTPUT_S3_REGION=<\optional\> [string] <br/>

The docker image can then be started with the following command (assuming all variables are stored in the file envVars):
> docker run --detach --env-file envVars --name \<container-name\> pyswim-img

Make sure to replace \<container-name\> with your desired container name, like 
> docker run --detach --env-file envVars --name swim-enroute-nas pyswim-img

When saving to a local file system, you can bind the host location to container's \data folder where all data is saved to.
> docker run --detach --env-file envVars --mount type=bind,src=<abs path>,dst=/data --name swim-enroute-nas pyswim-img 

where "src=\<abs path\>" refers to the absolute path location on the host, while "dst" refers to the default storage location in the container (do not change dst=/data). 

  
## Runtime options
One key option is to set the runtime of the FAA SWIM listener.  For a standard deployment, adjusting the option RUNTIME in the file configVars.cfg determines how many minutes the rcvr.py script will run.
  
In the case of the docker deployment it is important to change runtime related values in two places.  (1) docker/envVars; and (2) docker/rcvr-cron. This is because the docker deployment is designed to run indefinetely, which is achieved by calling running rcvr.py repeatedly using cron jobs.  As such, the cron command in docker/rcvr-cron need to reflect and match how long the listener is running before disconnecting.
  
By default RUNTIME = 1 (minutes), with the cron job calling rcvr.py every minute.  While there is a little delay in starting up the rcvr.py script and connecting to the FAA SWIM publisher, the delay is not problematic as the expiration time for messages within the queues are all at least 10 seconds (see the table below).  The benefit of running the code using a crob job is that if the connection is disrupted or a fault appears causing the code the crash, only data missing is data assocaited with the period of the failure.  Once the crob job is run again the connection can be reestablished.
  
  <img src="https://user-images.githubusercontent.com/44214575/200968359-8b787342-39ca-4c8d-b796-9d28d44baa83.png" width="200" />

  In the cases of data heavy streams, or if the code based is expanded to include real-time processing, then multiple instances of this container can be deployed.  In the case of multiple the messages will only be consumed only once; each instance of the container will receive unique data.
  
  ## Bucket Naming Convention
  The variable OUTPUT_S3_BUCKET_NAME can be set to create a new bucket based on the date (assuming OUTPUT_S3_MAKE_BUCKET=true).  For example, data can be stored in buckets for each day of the year: asde-x_010122,asde-x_010222, ... , asde-x_123122.  This is achieved by including the placeholders dd, mm, yy or yyyy in the variable that are replaced with the time formating strings %d, %m, %y and %Y;  make sure dd, mm, yy, and yyyy do not appear elsewhere in the bucket name.  Examples include:
  * OUTPUT_S3_BUCKET_NAME = asde-x_mmddyy
  * OUTPUT_S3_BUCKET_NAME = asde-x_mm-yyyyy
  * OUTPUT_S3_BUCKET_NAME = asde-x_yy_onlyDFW
  * OUTPUT_S3_BUCKET_NAME = yyyy-etms
  * OUTPUT_S3_BUCKET_NAME = dd-mm-yyyy-etms
  
  The dd, mm, yy, and yyyy placeholders can be located anywhere in the bucket name, in any order, and include additional separating charactors as desired.
  
  
  
  

  
