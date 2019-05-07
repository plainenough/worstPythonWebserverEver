FROM ubuntu:bionic
MAINTAINER derrickwalton

USER root
RUN apt-get update && \
apt-get -y install python3 python3-yaml git
RUN rm -rf /var/www/html
RUN git clone https://github.com/plainenough/worstPythonWebserverEver.git /var/www/html

EXPOSE 80
CMD cd /var/www/html && python3 wpwe
