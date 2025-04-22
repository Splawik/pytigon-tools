export TWINE_USERNAME=__token__
export TWINE_PASSWORD=***
cd pytigon-lib
twine upload --repository pytigon-lib dist/*
cd ..
cd pytigon
twine upload --repository pytigon dist/*
cd ..
cd pytigon-batteries
twine upload --repository pytigon-batteries dist/*
cd ..
cd pytigon-gui
twine upload --repository pytigon-gui dist/*
cd ..
