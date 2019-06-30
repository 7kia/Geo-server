ARG pyversion=2.7
FROM python:${pyversion}-stretch
ARG pyversion=2.7
ENV PYVERSION ${pyversion:-2.7}

# Install packages
RUN apt-get -yqq update && \
    apt-get -yqq install apache2 apache2-dev locales && \
    apt-get clean

# Install locale
COPY ./locale.gen /etc/locale.gen
RUN locale-gen

# Install venv
RUN pip install virtualenv

# Prepare virtualenv
RUN mkdir /app
WORKDIR /app

COPY . /app

RUN virtualenv env
RUN ls
RUN ./env/bin/pip install --upgrade pip setuptools

# Install mod_wsgi
RUN ./env/bin/pip install mod_wsgi


# Prepare app directory
RUN mkdir ./pylibs

# Configure Apache
COPY ./start-apache.sh /
COPY ./wsgi.conf.tmpl /tmp/wsgi.conf.tmpl
RUN sed -e s/\$PYVERSION/$PYVERSION/g /tmp/wsgi.conf.tmpl | sed -e s/\$PYV/`echo $PYVERSION | sed -e "s/\\.//"`/g >/etc/apache2/mods-enabled/wsgi.conf
ONBUILD COPY apache.conf /etc/apache2/sites-available/000-default.conf

VOLUME  /app /home/war-on-map/Geo-server

# Start Apache
EXPOSE 8080
CMD ["/bin/sh", "-c","/start-apache.sh"]
