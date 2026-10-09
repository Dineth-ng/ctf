FROM php:8.2-apache
RUN docker-php-ext-install mysqli
COPY apache.conf /etc/apache2/conf-enabled/stage4.conf
COPY php.ini /usr/local/etc/php/conf.d/stage4.ini
COPY src/ /var/www/html/
COPY app/ /opt/stage4/
