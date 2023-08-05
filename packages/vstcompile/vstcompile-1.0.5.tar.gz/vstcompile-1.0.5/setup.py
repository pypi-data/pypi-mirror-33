import os

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
from vstcompile import load_requirements, make_setup

make_setup(
    py_modules=['vstcompile'],
    include_package_data=True,
    install_requires=[],
    extras_require={
        'compile': load_requirements('requirements.txt'),
        'doc':
            load_requirements('requirements-doc.txt') +
            load_requirements('requirements.txt'),
        'release': load_requirements('requirements-release.txt'),
    },
    project_urls={
        "Issue Tracker": "https://gitlab.com/vstconsulting/vstcompile/issues",
        "Source Code": "https://gitlab.com/vstconsulting/vstcompile",
        "Releases": "https://pypi.org/project/vstcompile/#history",
    },
)
