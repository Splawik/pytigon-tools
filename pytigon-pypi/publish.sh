export TWINE_USERNAME=__token__
export TWINE_PASSWORD=***
cd pytigon-lib
twine upload dist/*
cd ..
cd pytigon
twine upload dist/*
cd ..
cd pytigon-batteries
twine upload dist/*
cd ..
cd pytigon-gui
twine upload dist/*
cd ..
