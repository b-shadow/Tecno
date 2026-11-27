FROM php:8.3-cli

RUN apt-get update && apt-get install -y \
    libpq-dev \
    zip \
    unzip \
    git \
    && docker-php-ext-install pdo pdo_pgsql

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /app

# El servidor de desarrollo (php -S) corre en la SAPI CLI: sin esto cada peticion recompila Laravel (~3 s).
RUN echo "opcache.enable_cli=1" > /usr/local/etc/php/conf.d/opcache-cli.ini
