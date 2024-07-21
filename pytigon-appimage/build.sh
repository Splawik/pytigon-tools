docker build . -f Dockerfile -t pytigon-appimage:latest
docker run -it --cap-add SYS_ADMIN --device /dev/fuse --security-opt apparmor:unconfined --mount type=bind,source="$(pwd)",target=/app/out pytigon-appimage:latest
     