@echo off

call :getUTCTime
echo %UTCTIMESTR%
echo %UTCTIMESTR%> ./dependency/utc_time.txt

exit /b

:getUTCTime
FOR /F "usebackq tokens=1,2 delims==" %%i IN (`wmic path win32_utctime get /format:list^|find "="`) DO (
  if "%%i" EQU "Year" set YY=%%j
  if "%%i" EQU "Month" set MM=%%j
  if "%%i" EQU "Day" set DD=%%j
  if "%%i" EQU "Hour" set HH=%%j
  if "%%i" EQU "Minute" set MI=%%j
  if "%%i" EQU "Second" set SS=%%j
  if "%%i" EQU "DayOfWeek" set DW=%%j
)
if %MM% LSS 10 set MM=0%MM%
if %DD% LSS 10 set DD=0%DD%
if %HH% LSS 10 set HH=0%HH%
if %MI% LSS 10 set MI=0%MI%
if %SS% LSS 10 set SS=0%SS%

if "%DW%" EQU "1" set DWS=MON
if "%DW%" EQU "2" set DWS=TUE
if "%DW%" EQU "3" set DWS=WED
if "%DW%" EQU "4" set DWS=THU
if "%DW%" EQU "5" set DWS=FRI
if "%DW%" EQU "6" set DWS=SAT
if "%DW%" EQU "7" set DWS=SUN

set UTCDATE=%YY%-%MM%-%DD%
set UTCTIME=%HH%.%MI%.%SS%
set UTCTIMESTR=%UTCDATE%_%UTCTIME%_%DWS%_UTC0
exit /b