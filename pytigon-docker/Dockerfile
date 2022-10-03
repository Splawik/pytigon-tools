ARG python_version=3.10

FROM python:${python_version} as build

RUN apt-get install -y curl git apt-transport-https 

RUN apt-get update -y

RUN pip install --upgrade pip

RUN pip install pytigon-batteries
RUN pip install git+https://github.com/Splawik/pytigon-batteries.git --upgrade
RUN pip uninstall pytigon -y
RUN pip install git+https://github.com/Splawik/pytigon.git
RUN pip uninstall pytigon-lib -y
RUN pip install git+https://github.com/Splawik/pytigon-lib.git

RUN pip install psycopg2-binary channels_redis graphviz


FROM python:${python_version}-slim

ARG python_version=3.10

RUN apt-get update -y

RUN apt-get install -y redis-server nginx 
#RUN wget https://github.com/dtalens/nginx-naxsi-deb/releases/download/1.17.10-0.56/nginx_1.17.10-1_amd64.deb
#RUN apt-get install ./nginx_1.17.10-1_amd64.deb -y --allow-downgrades

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

RUN pip install gunicorn uvicorn waitress

COPY --from=build /usr/local/lib/python${python_version}/site-packages/ /usr/local/lib/python${python_version}/site-packages/

RUN apt-get install git -y
RUN pip install git+https://github.com/graphql-python/graphene-django.git
RUN pip install git+https://github.com/silviolleite/django-pwa.git

EXPOSE 80
EXPOSE 443

CMD ["python", "entrypoint-interface.py"]
