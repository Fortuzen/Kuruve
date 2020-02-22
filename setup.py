from setuptools import setup
from setuptools import find_packages

import os
on_rtd = os.environ.get('READTHEDOCS') == 'True'
reqs = []
if not on_rtd:
    reqs = ["pygame", "numpy", "gym"]

setup(
    name='kuruve',
    version='',
    url='https://github.com/Fortuzen/Kuruve',
    license='',
    author='Fortuzen',
    author_email='',
    description='Kuruve learning environment. Achtung Die Kurve clone.',
    packages=find_packages(),
    package_data={'kuruve': ['maps/*.png']},
    include_package_data=True,
    install_requires=reqs
)
