ARG python_version=3.12

FROM python:${python_version} as build

RUN apt-get install -y curl git apt-transport-https 

RUN apt-get update -y

RUN pip install --upgrade pip

RUN pip install cryptography

RUN pip install pytigon-lib
RUN pip install pytigon
RUN pip install pytigon-batteries[all]

RUN pip install psycopg2-binary channels_redis sentry-sdk django-prometheus python3-openid

RUN pip install git+https://github.com/Splawik/pytigon.git --upgrade --force-reinstall
RUN pip install git+https://github.com/Splawik/pytigon-lib.git --upgrade --force-reinstall


FROM python:${python_version}-slim

ARG python_version=3.12

RUN apt-get update -y

RUN apt-get install -y redis-server nginx 

RUN apt-get -y install postgresql-client postgresql-client-common libpq-dev

RUN mkdir -p /home/www-data/pytigon/ext_prg
RUN mkdir -p /home/www-data/.pytigon/temp

ADD ./entrypoint-interface.py /home/www-data/pytigon/entrypoint-interface.py
ADD ./entrypoint-interface-scheduler.sh /home/www-data/pytigon/entrypoint-interface-scheduler.sh

WORKDIR /home/www-data/pytigon

RUN chown -R www-data:www-data /home/www-data && \
    usermod -d /home/www-data www-data && \
    ln -s /etc/nginx/sites-available/pytigon /etc/nginx/sites-enabled/pytigon && \
    rm /etc/nginx/sites-available/default && \
    rm /etc/nginx/sites-enabled/default

RUN pip install gunicorn

COPY --from=build /usr/local/lib/python${python_version}/site-packages/ /usr/local/lib/python${python_version}/site-packages/
COPY --from=build /usr/local/bin/ptig /usr/local/bin/

RUN apt-get install git -y
RUN apt install -y libcairo2


EXPOSE 80
EXPOSE 443

CMD ["python", "entrypoint-interface.py"]
