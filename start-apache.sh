#!/bin/sh

set -e

. /etc/apache2/envvars

mkdir /var/run/apache2
mkdir /var/lock/apache2
chown root:/var/www/geoserver /var/lock/apache2
exec /usr/sbin/apache2 -k start -DFOREGROUND
