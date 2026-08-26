"""
TypeMaster build script for packaging the application into a standalone EXE.
Installs PyInstaller, compiles resources, and runs the compiler.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def build():
    # 1. Setup paths
    base_dir = Path(__file__).resolve().parent
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"

    # Clean previous builds
    for path in [dist_dir, build_dir]:
        if path.exists():
            print(f"Cleaning path: {path}")
            shutil.rmtree(path, ignore_errors=True)

    # 2. Install PyInstaller into virtual environment
    print("Verifying PyInstaller installation...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    except subprocess.CalledProcessError as err:
        print(f"Failed to install PyInstaller: {err}")
        sys.exit(1)

    # 3. Resolve PyInstaller executable path
    venv_bin_dir = Path(sys.executable).parent
    pyinstaller_exe = venv_bin_dir / "pyinstaller.exe"
    if not pyinstaller_exe.exists():
        pyinstaller_exe = venv_bin_dir / "pyinstaller"
    
    if not pyinstaller_exe.exists():
        # Fallback to system command search
        pyinstaller_exe = "pyinstaller"

    print(f"Using PyInstaller executable: {pyinstaller_exe}")

    # 4. Execute compilation command
    # Windows uses semicolon (;) to separate source and destination for --add-data
    cmd = [
        str(pyinstaller_exe),
        "--onefile",
        "--noconsole",
        "--name=TypeMaster",
        "--add-data=assets;assets",
        "main.py"
    ]

    print(f"Running command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print(f"Standalone executable generated at: {dist_dir / 'TypeMaster.exe'}")
        print("="*50)
    except subprocess.CalledProcessError as err:
        print(f"PyInstaller build failed: {err}")
        sys.exit(1)

if __name__ == "__main__":
    build()
