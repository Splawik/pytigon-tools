docker build . -f Dockerfile -t pytigon-appimage:latest
docker run -it --mount type=bind,source="$(pwd)",target=/app/out pytigon-appimage:latest
