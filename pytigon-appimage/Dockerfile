FROM python:3.7-buster

RUN mkdir -p /app
WORKDIR /app
RUN wget https://raw.githubusercontent.com/AppImage/pkg2appimage/master/pkg2appimage
RUN chmod +rwx pkg2appimage
RUN apt update
RUN apt-get install -y desktop-file-utils virtualenv libfuse2
ADD ./recipes/pytigon.yml /app/pytigon.yml
#ADD ./recipes/excludelist /app/excludelist
CMD ./pkg2appimage pytigon.yml
