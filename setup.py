import sys,os
from cx_Freeze import setup, Executable
import subprocess



build_exe_options = {
    "packages": ["os"],
    'zip_include_packages':[],
    "excludes": ["Tkinter","Tkinter","matplotlib",'numpy'],
    "includes": [],
    "include_files":[
        'C:/Users/b.lecoquil/AppData/Local/Programs/Python/Python38-32/DLLs/tcl86t.dll',
        'C:/Users/b.lecoquil/AppData/Local/Programs/Python/Python38-32/DLLs/tk86t.dll',
        ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

os.environ['TCL_LIBRARY'] = "C:/Users/b.lecoquil/AppData/Local/Programs/Python/Python38-32/tcl/tcl8.6"
os.environ['TK_LIBRARY'] = "C:/Users/b.lecoquil/AppData/Local/Programs/Python/Python38-32/tcl/tk8.6"

setup(  name = "AppLidar",
        version = "0.1",
        author = "Blaise Le Coquil",
        description = "Script pour la génération de scans lidar",
        options = {"build_exe": build_exe_options},
        executables = [Executable("AppLidar.py", base=base, icon="icone.ico")])
