.\ext_prg\tcc\tcc ptig.c -o ptig.exe
.\ext_prg\tcc\tcc ptigw.c -o ptigw.exe
.\ext_prg\rcedit "ptigw.exe" --set-icon "python\lib\site-packages\pytigon\pytigon.ico"
.\python\python -m pip install pywin32
.\python\python -m pip uninstall pytigon-gui
.\python\python -m pip install git+https://github.com/Splawik/pytigon-gui.git
.\python\python -m pip uninstall pytigon
.\python\python -m pip install git+https://github.com/Splawik/pytigon.git
.\python\python -m pip uninstall pytigon-lib
.\python\python -m pip install git+https://github.com/Splawik/pytigon-lib.git
