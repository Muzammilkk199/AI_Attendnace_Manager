@echo off
echo Starting AI Attendance Manager Server...
echo.

REM Activate virtual environment
echo Activating virtual environment...
call D:\Techwiz\env\Scripts\activate.bat

REM Check if Django is available
echo Checking Django installation...
python -c "import django; print('Django version:', django.get_version())"

REM Start Django server
echo.
echo Starting Django development server...
echo Server will be available at: http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

pause
