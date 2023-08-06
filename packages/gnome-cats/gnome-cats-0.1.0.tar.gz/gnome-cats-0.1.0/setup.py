from setuptools import setup, find_packages
from os import path


currdir = path.abspath(path.dirname(__file__))
with open(path.join(currdir, 'README.md')) as f:
    long_desc = f.read()

setup(
    name='gnome-cats',
    version='0.1.0',
    description='Bring cats to your desktop',
    author='Juanjo Salvador',
    author_email='juanjosalvador@netc.eu',
    packages=find_packages(),
    package_data={'gnomeCats':['application.ui']},
    classifiers=[
        'Development Status :: 1 - Planning',
    ],
    scripts=['bin/gnome-cats'],
    long_description=long_desc,
    long_description_content_type='text/markdown',
    python_requires='>=3',
    install_requires=[
        'PyGObject==3.28.1',
    ],
)
