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
python ptig.py manage__schall compiletemplates
python ptig.py manage__schdata compiletemplates
python ptig.py manage__schremote compiletemplates
python ptig.py manage__schserverless compiletemplates
python ptig.py manage__schtools compiletemplates
python ptig.py manage__schwiki compiletemplates
python ptig.py manage__schplaywright compiletemplates
python ptig.py manage_schdevtools compiletemplates
python ptig.py manage__schsetup compiletemplates
python ptig.py manage__schcomponents compiletemplates
python ptig.py manage_scheditor compiletemplates
python ptig.py manage_schemail compiletemplates
python ptig.py manage_schodf compiletemplates
python ptig.py manage_schportal compiletemplates
python ptig.py manage_schpytigondemo compiletemplates
python ptig.py manage_schwebtrapper compiletemplates
echo "pytigon step 4"
cd ..
rm -R ./build
rm -R ./dist
python setup.py sdist bdist_wheel
cd ..
cd pytigon-batteries
git pull
rm -R ./build
rm -R ./dist
python setup.py sdist bdist_wheel
cd ..
cd pytigon-gui
git pull
rm -R ./build
rm -R ./dist
python setup.py sdist bdist_wheel
cd ..
