; Include Modern User Interface
!include "MUI2.nsh"

; Define Product Information
!define PRODUCT_NAME "ECMConfig"
!define PRODUCT_VERSION "1.1.4"
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "ECMConfigSetup.exe"
InstallDir "$PROGRAMFILES\ECMConfig"
RequestExecutionLevel admin ; Request admin privileges for installation

; Interface Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Define Supported Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Spanish"

; Enable Language Selection Dialog in Initialization Function
Function .onInit
    ; Save the selected language in the registry
    !define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
    !define MUI_LANGDLL_REGISTRY_KEY "Software\${PRODUCT_NAME}\Installer"
    !define MUI_LANGDLL_REGISTRY_VALUENAME "UILanguage"
    !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

; LangString Definitions
LangString MUI_TEXT_WELCOME_INFO_TITLE ${LANG_ENGLISH} "Welcome to the ECM Config Setup Wizard"
LangString MUI_TEXT_WELCOME_INFO_TITLE ${LANG_SPANISH} "Bienvenido al asistente de instalación de ECM Config"

LangString MUI_TEXT_WELCOME_INFO_TEXT ${LANG_ENGLISH} "This wizard will guide you through the installation."
LangString MUI_TEXT_WELCOME_INFO_TEXT ${LANG_SPANISH} "Este asistente le guiará a través de la instalación."

LangString MUI_TEXT_FINISH_TITLE ${LANG_ENGLISH} "Installation Complete"
LangString MUI_TEXT_FINISH_TITLE ${LANG_SPANISH} "Instalación completa"

LangString MUI_TEXT_FINISH_INFO_TEXT ${LANG_ENGLISH} "ECM Config has been installed successfully."
LangString MUI_TEXT_FINISH_INFO_TEXT ${LANG_SPANISH} "ECM Config se ha instalado correctamente."

Section "Install ECM Config"
    SetOutPath "$INSTDIR"
    ; Copy the PyInstaller output (which now contains the exe and other files)
    File /r "C:\Users\joben\EAT\ECM\SW\ecm_field_app\dist\ecm_config\*.*"
    ; Manually copy the assets folder from your project directory to the install folder
    CreateDirectory "$INSTDIR\assets"
    File /r "C:\Users\joben\EAT\ECM\SW\ecm_field_app\assets\*.*"
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Register the application in Windows for Apps & Features
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME} ${PRODUCT_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayIcon" "$INSTDIR\ecm_config.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoRepair" 1

    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Start Menu Shortcuts"
    SetShellVarContext all
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\ecm_config.exe"
SectionEnd

Section "Uninstall"
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk"
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
    RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
    ; Remove registry uninstall entry
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
    RMDir /r "$INSTDIR"
SectionEnd
