alias python="python3.12"
cd pytigon-lib
git pull
rm -R ./build
rm -R ./dist
python setup.py sdist bdist_wheel
cd ..
cd pytigon
echo "pytigon step 1"
git pull
export PYTHONPATH=$(pwd)/../pytigon-lib
echo "pytigon step 2"
bash prepare_for_pypi.sh
cd pytigon
echo "pytigon step 3"
ptig ptig.py manage__schall compiletemplates
ptig ptig.py manage__schdata compiletemplates
ptig ptig.py manage__schremote compiletemplates
ptig ptig.py manage__schserverless compiletemplates
ptig ptig.py manage__schtools compiletemplates
ptig ptig.py manage__schwiki compiletemplates
ptig ptig.py manage__schplaywright compiletemplates
ptig ptig.py manage_schdevtools compiletemplates
ptig ptig.py manage__schsetup compiletemplates
ptig ptig.py manage__schcomponents compiletemplates
ptig ptig.py manage_scheditor compiletemplates
ptig ptig.py manage_schemail compiletemplates
ptig ptig.py manage_schodf compiletemplates
ptig ptig.py manage_schportal compiletemplates
ptig ptig.py manage_schpytigondemo compiletemplates
ptig ptig.py manage_schwebtrapper compiletemplates
echo "pytigon step 4"
cd ..
rm -R ./build
rm -R ./dist
ptig setup.py sdist bdist_wheel
cd ..
cd pytigon-batteries
git pull
rm -R ./build
rm -R ./dist
ptig setup.py sdist bdist_wheel
cd ..
cd pytigon-gui
git pull
rm -R ./build
rm -R ./dist
ptig setup.py sdist bdist_wheel
cd ..
