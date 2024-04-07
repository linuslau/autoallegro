pyinstaller -F main.py --add-data "dependency;dependency" --add-data "icon;icon" -n AutoAllegro --uac-admin --icon .\icon\logo_main.png --splash .\icon\logo_splash.png -w
pause