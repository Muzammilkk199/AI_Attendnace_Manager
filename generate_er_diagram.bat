@echo off
echo ========================================
echo AI Attendance Manager - ER Diagram Generator
echo ========================================
echo.

echo Installing required packages...
pip install matplotlib numpy

echo.
echo Generating ER Diagram...
python simple_er_diagram_generator.py

echo.
echo ========================================
echo ER Diagram generation completed!
echo Check the generated files:
echo - ai_attendance_er_diagram.png
echo - ai_attendance_er_diagram.pdf
echo - ai_attendance_er_diagram.svg
echo ========================================
pause
