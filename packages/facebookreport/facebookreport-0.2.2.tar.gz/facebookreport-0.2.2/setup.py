from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "facebookreport",
    version = "0.2.2",
    author = "Daniel Corvalán",
    author_email = "corvalanlara@protonmail.com",
    description = "App for creating a Facebook fanpage performance report",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/corvalanlara/",
    packages = find_packages(),
    entry_points = {
        'gui_scripts':[
            'facebookreport = facebookreport.reportmaker:main'
        ]
    },
    install_requires = ['pandas', 'matplotlib', 'python-docx'],
    include_package_data = True,
    package_data = {
        'facebookreport' : ['cuentas'],
    },
    classifiers = (
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ),
)
