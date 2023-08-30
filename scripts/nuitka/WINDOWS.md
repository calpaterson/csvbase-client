# Instructions for building on Windows

1. Make sure Python is installed, either conda or from python.org
2. Make venv: `python -mv venv windows-venv`
3. Activate it: `venv\Scripts\activate`
4. `python -m pip install --upgrade pip setuptools wheel`
5. `python -m pip install -e .`
6. `python -m pip install nuitka`
7. `python -m nuitka --follow-imports --standalone --onefile scripts\nuitka\trampoline.py -o csvbase-client.exe`

The first time you do step #7 you will probably need to agree to download
mingw, ccache and dependency walker.
