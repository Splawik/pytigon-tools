export $(grep -v '^#' .env | xargs)
cd pytigon-lib
uv publish --token $TWINE_PASSWORD
cd ..
cd pytigon-standard-prj
uv publish --token $TWINE_PASSWORD
cd ..
cd pytigon
uv publish --token $TWINE_PASSWORD
cd ..
cd pytigon-batteries
uv publish --token $TWINE_PASSWORD
cd ..
cd pytigon-gui
uv publish --token $TWINE_PASSWORD
cd ..
