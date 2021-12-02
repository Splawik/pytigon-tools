FROM python:3.9 as build

RUN apt-get install -y curl git apt-transport-https 

RUN apt-get update -y

RUN pip install --upgrade pip
RUN pip install "Twisted[tls,http2]==21.7.0"
RUN pip install "uvicorn<0.12"

RUN pip install pytigon-batteries
RUN echo "1"
RUN pip install git+https://github.com/Splawik/pytigon-batteries.git
RUN pip uninstall pytigon -y
RUN pip install git+https://github.com/Splawik/pytigon.git
RUN pip uninstall pytigon-lib -y
RUN pip install git+https://github.com/Splawik/pytigon-lib.git

RUN pip install psycopg2-binary channels_redis graphviz psutil

FROM python:3.9-slim

RUN apt-get update -y
RUN apt-get install -y redis-server nginx tcc
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

COPY --from=build /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

EXPOSE 80
EXPOSE 443

CMD ["python", "entrypoint-interface.py"]
