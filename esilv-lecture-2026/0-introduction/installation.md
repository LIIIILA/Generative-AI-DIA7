# Pre-requisite for all modes of installation

1. INSTALL Python 3.13 if not installed already: https://www.python.org/downloads/latest/python3.13/

2. Depending on your OS, open a terminal (CMD.exe in Windows, Terminal in MacOS/Linux) and check that Python is well integrated to the path:
```
python --version
```
WARNING! If you have several versions of Python installed, you may have to specify the full path of the right Python executable.

3. Download the zip archive of the course and unzip its content in the working directory of your choice.

4. Depending on your OS, open a terminal (CMD.exe in Windows, Terminal in MacOS/Linux) 

5. Go to the working directory just created and change directory to the root directory of the archive, called "esilv-lecture-2026". Accordingly, the content of your current directory should be a list of 2 subfolders: "0-introduction", "1-simpy" 

Continue below the installation procedure that best fits your preference.  
  
      
# Default install (recommended!)

6. Install jupyter lab:
```
pip install --user jupyterlab
```

7. Install the Graphviz application separately from the Python `graphviz` package. The Python package does not include the `dot` executable used to render graphs.
Skip this step if you enter into too many difficulties, it is requested mostly for lecture-SymPy-5.ipynb activity.  
- Windows (CMD):
```
winget install --id Graphviz.Graphviz --exact --source winget
```
Add graphviz binary executable to PATH:
```
set "PATH=C:\Program Files\Graphviz\bin;%PATH%"
```
Verify that the executable is now accessible:
```
dot -V
```
- MacOS (Terminal, with Homebrew):
```
brew install graphviz
export PATH="$(brew --prefix)/bin:$PATH"
```
- Linux (Debian/Ubuntu):
```
sudo apt update
sudo apt install graphviz
export PATH="/usr/bin:$PATH"
```
On Fedora, use `sudo dnf install graphviz` instead of the `apt` commands. To make a PATH update persistent, add the corresponding `export PATH=...` line to your shell startup file (for example, `~/.zshrc` or `~/.bashrc`).
Verify that the executable is now accessible:
```
dot -V
```

If JupyterLab is already running, shut down its server and launch it again from the terminal where `dot -V` succeeds. Restarting only the notebook kernel or refreshing the browser does not update the server's inherited PATH.


8. Check that jupyterlab is correctly installed by launching it from your current folder:
```
python -m jupyterlab  
```
You are from now in the default browser with a jupyterlab interface displayed!
(online documentation: https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html)

9. In the jupyterlab interface, browse folders and open notebook 0-introduction/solutions/checking-notebook.ipynb

10. Run all the cells of the notebook (select Run -> Run All Cells) and check all cells have been correctly executed.

11. Likewise, go back to the root folder and open now the notebook 1-sympy/exercices/lecture-SymPy-1_exo.ipynb.

12. Run all the cells of this notebook and check all cells have been correctly executed.

Well done!!! You are ready to begin the exercises.
  
  
# Install with virtual environment support

Follow this procedure if you prefer not to install jupyterlab, sympy, etc. at the global level, to avoid potential conflicts of versions with other libraries installed at the global level.
  
Create within the current directory a virtual environment associated to subfolder ".venv" that will host binaries and dependencies.
Reminder: If you have several Python versions, specify the absolute path of the Python executable.
```
python -m venv .venv
```

Depending on your OS, activate the virtual environment:
- Windows:
```
.venv\scripts\activate.bat
```
- MacOS (Terminal, zsh or bash):
```
source .venv/bin/activate
```
- Linux (Debian/Ubuntu, Fedora, and other distributions; bash or zsh):
```
source .venv/bin/activate
```
The activation command is the same across these MacOS and Linux distributions.

The system prompt should now display a virtual environment prefix.
  
Continue from the beginning of the default install (step 6.).