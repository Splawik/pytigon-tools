alias python="python3.14"
export PYTIGON_PRJ_PATH=$(pwd)/pytigon-standard-prj/pytigon_standard_prj/prj
export PYTHONPATH=$(pwd)/pytigon-lib:$(pwd)/pytigon:$PYTIGON_PRJ_PATH

echo $PYTIGON_PRJ_PATH
echo $PYTHONPATH

cd pytigon-lib
git pull
rm -R ./build
rm -R ./dist
rm -rf /tmp/build-env-* pytigon_lib.egg-info dist
ptig python -m build
cd ..

cd pytigon-standard-prj
git pull
rm -R ./build
rm -R ./dist
ptig python -m build
cd ..

cd pytigon
echo "pytigon step 1"
git pull
echo "pytigon step 2"
bash prepare_for_pypi.sh
cd pytigon
echo "pytigon step 3"
ptig manage__schall compiletemplates
ptig manage__schdata compiletemplates
ptig manage__schremote compiletemplates
ptig manage__schserverless compiletemplates
ptig manage__schtools compiletemplates
ptig manage__schwiki compiletemplates
ptig manage__schplaywright compiletemplates
ptig manage_schdevtools compiletemplates
ptig manage__schsetup compiletemplates
ptig manage__schcomponents compiletemplates
ptig manage_scheditor compiletemplates
ptig manage_schemail compiletemplates
ptig manage_schodf compiletemplates
ptig manage_schportal compiletemplates
ptig manage_schpytigondemo compiletemplates
ptig manage_schwebtrapper compiletemplates
echo "pytigon step 4"
cd ..
rm -R ./build
rm -R ./dist
ptig python -m build
cd ..
cd pytigon-batteries
git pull
rm -R ./build
rm -R ./dist
ptig python -m build
cd ..
cd pytigon-gui
git pull
rm -R ./build
rm -R ./dist
ptig python -m build
cd ..
