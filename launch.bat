echo "Lauching..."
@echo off
if defined ProgramFiles(x86) (
    set PYSDL2_DLL_PATH=%cd%\dll\x64\
) else (
    set PYSDL2_DLL_PATH=%cd%\dll\x64\
)
python "source/state.py"
