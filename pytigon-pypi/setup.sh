cd pytigon-lib
git pull
rm -R ./build
rm -R ./dist
python3.9 setup.py sdist bdist_wheel
cd ..
cd pytigon
git pull
cd pytigon
export PYTHONPATH=../../pytigon-lib
python3.9 manage.py compile_templates
cd ..
rm -R ./build
rm -R ./dist
python3.9 setup.py sdist bdist_wheel
cd ..
cd pytigon-batteries
git pull
rm -R ./build
rm -R ./dist
python3.9 setup.py sdist bdist_wheel
cd ..
cd pytigon-gui
git pull
rm -R ./build
rm -R ./dist
python3.9 setup.py sdist bdist_wheel
cd ..
