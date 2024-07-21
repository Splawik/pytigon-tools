Unicode true
SetCompressor /SOLID lzma
;SetCompress off

!include "MUI2.nsh"

Name "Pytigon"

OutFile ".\install\install_pytigon.exe"
InstallDir "$LOCALAPPDATA\pytigon"
InstallDirRegKey HKCU "Software\pytigon" ""
RequestExecutionLevel user

InstType "$(Pytigon)"
InstType "$(Visual C++ Redistributable)"

!define COMPANYNAME "Pytigon"
!define MUI_ABORTWARNING
!define MUI_LANGDLL_ALLLANGUAGES

;--------------------------------
;Pages
  !insertmacro MUI_PAGE_LICENSE "LICENSE"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
;--------------------------------
;Languages
  !insertmacro MUI_LANGUAGE "English"
  !insertmacro MUI_LANGUAGE "Polish"

;--------------------------------
;Installer Sections


Section "Pytigon"

  SectionIn 1
  SetOutPath $INSTDIR\python
  File /r /x *.pyo /x __pycache__  python\*.*
  ;SetOutPath $PROFILE\.pytigon\ext_prg
  ;File /r  /x __pycache__ /x *.pyc /x *.pyo ext_prg\*.*

  SetOutPath $INSTDIR
  File ptig.cmd
  File ptigw.exe
  File LICENSE

  ;Store installation folder
  WriteRegStr HKCU "Software\pytigon" "" $INSTDIR

  ReadRegStr $R0 HKCU "Software\Classes\.ptig" ""
  StrCmp $R0 "Software\Classes\Pytigon" 0 +1
  DeleteRegKey HKCU "Software\Classes\Pytigon.0"

  WriteRegStr HKCU "Software\Classes\.ptig" "" "Pytigon.0"
  WriteRegStr HKCU "Software\Classes\Pytigon.0" "" "Pytigon file"
  WriteRegStr HKCU "Software\Classes\Pytigon.0\DefaultIcon" "" "$INSTDIR\ptigw.exe,0"
  ReadRegStr $R0 HKCU "Software\Classes\Pytigon.0\shell\open\command" ""
  ${If} $R0 == ""
    WriteRegStr HKCU "Software\Classes\Pytigon.0\shell" "" "open"
    WriteRegStr HKCU "Software\Classes\Pytigon.0\shell\open\command" "" '$INSTDIR\ptigw.exe "%1"'
  ${EndIf}

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  EnVar::SetHKCU
  EnVar::AddValueEx "PATH" "$INSTDIR"

  WriteRegStr HKCU "Software\pytigon" "" $INSTDIR

  createDirectory "$SMPROGRAMS\${COMPANYNAME}"
  createShortCut "$SMPROGRAMS\${COMPANYNAME}\pytigon.lnk" "$INSTDIR\ptigw.exe" "" "$INSTDIR\ptigw.exe" 0 SW_SHOWNORMAL ALT|CONTROL|SHIFT|P "$(pytigon_description)"

SectionEnd

Section "Visual C++ Redistributable"
  SectionIn 2
  SetOutPath "$TEMP"
  File ".\install\vcredist_x64.exe"
  ExecWait '"$TEMP\vcredist_x64.exe" /passive /norestart'
  Delete "$TEMP\vcredist_x64.exe"
SectionEnd


;--------------------------------
;Uninstaller Section

Section "Uninstall"

  EnVar::SetHKCU
  EnVar::DeleteValue "PATH" "$INSTDIR"

  Delete "$INSTDIR\Uninstall.exe"

  RMDir /r /REBOOTOK $INSTDIR

  DeleteRegKey /ifempty HKCU "Software\pytigon"


SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString Pytigon ${LANG_ENGLISH} "Pytigon"
  LangString Pytigon ${LANG_POLISH} "Pytigon"
  LangString no_python_runtime ${LANG_ENGLISH} "Visual C++ Redistributable"
  LangString no_python_runtime ${LANG_POLISH} "Visual C++ Redistributable"
  LangString pytigon_description ${LANG_ENGLISH} "Start pytigon"
  LangString pytigon_description ${LANG_POLISH} "Start pytigon"
