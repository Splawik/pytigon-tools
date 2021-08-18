FROM python:3.7-buster

RUN mkdir -p /app
WORKDIR /app
RUN wget https://raw.githubusercontent.com/AppImage/pkg2appimage/master/pkg2appimage
RUN chmod +rwx pkg2appimage
RUN apt update
RUN apt-get install -y desktop-file-utils virtualenv
ADD ./recipes/pytigon.yml /app/pytigon.yml
#RUN ./pkg2appimage pytigon.yml

CMD ./pkg2appimage pytigon.yml
