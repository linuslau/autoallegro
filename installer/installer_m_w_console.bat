cd ../
pyinstaller -D main.py --add-data "dependency;dependency" --add-data "icon;icon" -n NetlistAutoMapper --uac-admin --icon .\icon\logo_main.png
pause