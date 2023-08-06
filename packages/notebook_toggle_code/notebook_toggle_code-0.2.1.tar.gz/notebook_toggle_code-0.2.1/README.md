# notebook-toggle-code

This is a Python package to allow code-toggle of code cells in a [Jupyter notebook](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html) by injection of javascript in an output cell. As a consequence for security reasons it only works in [**trusted** notebooks](http://jupyter-notebook.readthedocs.io/en/stable/security.html#security-in-notebook-documents).  

## 1 - Install

From terminal:

```bash
pip install notebook_toggle_code
```

## 2 - User Guide

In a notebook cell:

```Python
from notebook_toggle_code import ToggleCode
# example
ToggleCode(init_show=True, delay_toggle=0, verbose=False).add_js()
```

This will inject javascript code (in the output cell) with immediate effect.  
Upon notebook start the javascript will play upon the `app_initialized` event.  

The arguments are:
+ `init_show` (default=True) to define the initial state
+ `delay_toggle` (default=0) to set a progressive toggle in milliseconds
+ `verbose` (default=False) to show more info

To rid the notebook of the toggle-code feature just clear the output cell.

See the [demo notebook](http://nbviewer.jupyter.org/github/oscar6echo/notebook-toggle-code/blob/master/demo_toggle_code.ipynb)


## 3 - Security

Because a notebook is designed to allow the user to write arbitrary code, it has full access to many resources.   

The typical risks are the following:
+ A notebook has access to your file system and can therefore potentially read/modify/delete any of your files or send them to an attacker, or write a new file (virus).  
+ A notebook may contain javascript in output cells which can read you cookies and local storage and potentially send them to an attacker.  

See the [Security in notebook documents](https://jupyter-notebook.readthedocs.io/en/stable/security.html#security-in-notebook-documents) section of the official [Jupyter Notebook documentation](https://jupyter-notebook.readthedocs.io/en/stable/index.html) for more info.  

Therefore you **should review** and **must trust** the notebook before you can use **notebook-code-toggle**.


<!-- pandoc --from=markdown --to=rst --output=README.rst README.md -->
