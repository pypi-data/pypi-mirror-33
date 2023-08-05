from setuptools import setup
from glob import glob
import os


path = os.environ['FLORA_PORTAL_PATH']

setup(
    name='flora_portal',
    packages=['flora_portal'],
    include_package_data=True,
    zip_safe=False,
    data_files=[
        (os.path.join(path, 'static/css'), glob('static/css/*')),
        (os.path.join(path, 'static/js'), glob('static/js/*'))
    ],
    install_requires=[
        'flask',
        'flask-mysql',
        'pyaml',
        'bleach'
    ]
)

