FROM python:2.7.15-alpine as app

ENV TZ=Asia/Tehran


COPY ["wait-for.sh", "/"]

RUN addgroup -g 1000 www-data && adduser -u 1000 -HD -G www-data www-data && \
    mkdir -p /var/www && chown -R www-data:www-data /var/www/ && \
    apk add --no-cache --virtual .build-deps \
        linux-headers \
        musl-dev \
        gcc && \
    apk add --update --no-cache \
        postgresql-dev \
        tzdata && \
    pip install --no-cache-dir psycopg2==2.7.4 uWSGI==2.0.17.1 && \
    apk del .build-deps && \
    chmod +x /wait-for.sh && \
    rm -rf /var/cache/apk/* && \
    cd /root && rm -rf .cache && cd /

COPY ["entrypoint.sh", "./uwsgi.conf", "requirements.txt", "/"]

RUN pip install --no-cache-dir -r /requirements.txt && \
    cd /root && rm -rf .cache && \
    chmod +x /entrypoint.sh

COPY --chown=www-data:www-data . /var/www

USER www-data

WORKDIR /var/www

EXPOSE 9000

ENTRYPOINT exec /entrypoint.sh

FROM nginx:1.14.0-alpine as nginx

COPY --chown=nginx:nginx --from=app /var/www /var/www
COPY default.conf  /etc/nginx/conf.d/default.conf
RUN sed -i '/worker_processes  1;/c\worker_processes 4;' /etc/nginx/nginx.conf