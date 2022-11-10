FROM python:3.8

RUN apt-get update && apt-get install -y cron gcc g++ cmake cmake-curses-gui uuid-dev libssl-dev python3-dev swig pkg-config

# Update and install packages
RUN pip install --upgrade pip
ADD requirements.txt /requirements.txt
RUN pip install -r requirements.txt


# Create and Set directory
WORKDIR /data
WORKDIR /

# Copy files to root
COPY rcvr.py /rcvr.py
COPY wrtr.py /wrtr.py
COPY loadenv.py /loadenv.py
COPY docker/entrypoint.sh /entrypoint.sh

# Copy hello-cron file to the cron.d directory
COPY docker/rcvr-cron /etc/cron.d/rcvr-cron
 
# Give execution rights scripts
RUN chmod 0644 /etc/cron.d/rcvr-cron
RUN chmod +x /entrypoint.sh
 
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
 
# Run the command on container startup
ENTRYPOINT ["/entrypoint.sh"]