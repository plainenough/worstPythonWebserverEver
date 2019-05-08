FROM ubuntu:bionic
MAINTAINER derrickwalton

USER root
RUN apt-get update && \
apt-get -y install python3 python3-yaml git
RUN rm -rf /var/www/html
RUN git clone https://github.com/plainenough/worstPythonWebserverEver.git /var/www/html
COPY docker/include_config.yaml /var/www/html/config.yaml

EXPOSE 80
CMD cd /var/www/html && python3 wpwe -c /var/www/html/config.yaml

LABEL "version"="0.0.1"
LABEL "description"="This will simply reply with the originating request"
