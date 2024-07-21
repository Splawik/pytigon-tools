ptig zig rc ptigw.rc
ptig zig build-exe ptigw.c ptigw.res -target x86_64-windows-gnu --subsystem windows -lc
.\python\python -m pip install pywin32 --force
.\python\python -m pip install pytigon-gui --force
.\python\python -m pip install pytigon-batteries --force
.\python\python -m pip install pytigon --force
.\python\python -m pip install pytigon-lib --force
"C:\Program Files (x86)\NSIS\makensis.exe" pytigon.nsi
