VST Compile utility
===================

Lib for quick formatting `setup.py` in projects. Moved from `vstutils` projects for easyer integration.

Quick start
-----------

1. Install package via `pip install vstcompile`

2. Create `requirements.txt` and `setup.py` in your project:
   .. sourcecode:: python

      import os
      
      # allow setup.py to be run from any path
      
      os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

      from vstcompile import load_requirements, make_setup, find_packages

      ext_list = [
        ... some extentions import paths with `*.py, *.c or *.pyx` extentions ...
      ]
      
      make_setup(
        packages=find_packages(exclude=['tests']+ext_list),
        
        ext_modules_list=ext_list,
        
        include_package_data=True,
        
        install_requires=load_requirements('requirements.txt')
      )

3. Run `python setup.py compile` to compile and pack dist-package.


Requirements
------------

If you want to use Sphinx in projects, you should install package:

   .. sourcecode:: bash

      pip install vstcompile[doc]


LICENCE
-------

Apache Software License
