alias python="python3.13"
cd pytigon-lib
git pull
rm -R ./build
rm -R ./dist
#python setup.py sdist bdist_wheel
pptig python -m build
cd ..
cd pytigon
echo "pytigon step 1"
git pull
export PYTHONPATH=$(pwd)/../pytigon-lib
echo "pytigon step 2"
bash prepare_for_pypi.sh
cd pytigon
echo "pytigon step 3"
pptig ptig.py manage__schall compiletemplates
pptig ptig.py manage__schdata compiletemplates
pptig ptig.py manage__schremote compiletemplates
pptig ptig.py manage__schserverless compiletemplates
pptig ptig.py manage__schtools compiletemplates
pptig ptig.py manage__schwiki compiletemplates
pptig ptig.py manage__schplaywright compiletemplates
pptig ptig.py manage_schdevtools compiletemplates
pptig ptig.py manage__schsetup compiletemplates
pptig ptig.py manage__schcomponents compiletemplates
pptig ptig.py manage_scheditor compiletemplates
pptig ptig.py manage_schemail compiletemplates
pptig ptig.py manage_schodf compiletemplates
pptig ptig.py manage_schportal compiletemplates
pptig ptig.py manage_schpytigondemo compiletemplates
pptig ptig.py manage_schwebtrapper compiletemplates
echo "pytigon step 4"
cd ..
rm -R ./build
rm -R ./dist
#pptig setup.py sdist bdist_wheel
pptig python -m build
cd ..
cd pytigon-batteries
git pull
rm -R ./build
rm -R ./dist
#pptig setup.py sdist bdist_wheel
pptig python -m build
cd ..
cd pytigon-gui
git pull
rm -R ./build
rm -R ./dist
#pptig setup.py sdist bdist_wheel
pptig python -m build
cd ..
