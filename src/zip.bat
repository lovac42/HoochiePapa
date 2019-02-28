@echo off
set ZIP=C:\PROGRA~1\7-Zip\7z.exe a -tzip -y -r
set REPO=hoochiePapa

quick_manifest.exe "Hoochie Papa: NewQ" "hoochie_papa" >manifest.json

%ZIP% %REPO%_20.zip %REPO%.py

%ZIP% %REPO%_21.ankiaddon *.py manifest.json
