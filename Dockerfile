ARG pyversion=2.7
FROM python:${pyversion}-stretch
ARG pyversion=2.7
ENV PYVERSION ${pyversion:-2.7}

# Install packages
RUN apt-get -yqq update && \
    apt-get -yqq install apache2 apache2-dev locales && \
    apt-get clean



RUN apt-get install -y libapache2-mod-wsgi
RUN a2enmod wsgi
RUN service apache2 restart
RUN apt-get -yqq install libproj-dev
RUN apt-get -yqq install python-pyspatialite

# Install locale
COPY ./locale.gen /etc/locale.gen
RUN locale-gen


VOLUME /var/www/bases/ /var/www/bases/
COPY apache.conf.sample /etc/apache2/sites-available/000-default.conf

# Install venv
RUN pip2 install virtualenv
RUN pip2 install --upgrade virtualenv

# Prepare virtualenv
RUN mkdir /var/www/Geo-server
COPY . /var/www/Geo-server
WORKDIR /var/www/Geo-server

RUN virtualenv venv

RUN ./venv/bin/pip2 install --upgrade pip setuptools

# Install mod_wsgi
RUN ./venv/bin/pip2 install mod_wsgi

#RUN ./venv/bin/pip2 install git+https://github.com/lokkju/pyspatialite.git#egg=pyspatialite

RUN ls -c ./venv/lib/python2.7/site-packages
COPY pyspatialite ./venv/lib/python2.7/site-packages/pyspatialite





# Prepare app directory
RUN mkdir ./pylibs

# Configure Apache
COPY ./start-apache.sh /
COPY ./wsgi.conf.tmpl /tmp/wsgi.conf.tmpl
RUN sed -e s/\$PYVERSION/$PYVERSION/g /tmp/wsgi.conf.tmpl | sed -e s/\$PYV/`echo $PYVERSION | sed -e "s/\\.//"`/g >/etc/apache2/mods-enabled/wsgi.conf
#ONBUILD COPY apache.conf.sample /etc/apache2/sites-available/000-default.conf
VOLUME /home/war-on-map/Geo-server/ /var/www/Geo-server/

# Start Apache
EXPOSE 8080:8080
CMD ["/bin/sh", "-c","/start-apache.sh"]
