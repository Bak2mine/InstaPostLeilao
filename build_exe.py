"""
PyInstaller build script for Leiloaria Property PDF Generator

Usage:
    python build_exe.py

Creates standalone executable at:
    dist/leiloaria-generator.exe
"""

import subprocess
import sys
from pathlib import Path

def build_exe():
    """Build standalone EXE using PyInstaller"""

    # Get project directory
    project_dir = Path(__file__).parent

    # Clean previous builds to avoid PyInstaller cache conflicts
    build_dir = project_dir / "build"
    dist_dir = project_dir / "dist"

    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
        print(f"Cleaned build directory")

    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
        print(f"Cleaned dist directory")

    # PyInstaller command using spec file (which includes data files)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(project_dir / "leiloaria.spec"),
    ]

    print(f"Building EXE in: {project_dir}")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        exe_path = project_dir / "dist" / "leiloaria-generator.exe"
        print()
        print("=" * 70)
        print("[OK] Build successful!")
        print(f"  EXE location: {exe_path}")
        print()
        print("Usage:")
        print(f"  {exe_path}")
        print(f"  {exe_path} --limit 10")
        print(f"  {exe_path} --skip 50 --limit 20")
        print("=" * 70)
    else:
        print()
        print("[ERROR] Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
