import sys
from setuptools import setup, find_packages

sys.path.append('src')

setup(
    name="mw_jsons",
    version="0.0.2",
    author="Marlon Mendes",
    author_email="marlonciriatico@gmail.com",
    description="WebCrawler for genarating MatriculaWeb data",
    url="https://github.com/matwebapi/mwapi",
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points = {
              'console_scripts': [
                  'mw_jsons= mw_jsons.main:run',                  
              ],              
          },
)
