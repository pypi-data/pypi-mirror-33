from setuptools import setup
from os import path

# read the contents of your README file
ROOT_DIR = path.abspath(path.dirname(__file__))
with open(path.join(ROOT_DIR, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

test_requirements = ['pytest==3.6.2']

setup(
    name='declic',
    version='1.0.2',
    setup_requires=['pytest-runner', ],
    tests_require = test_requirements,
    py_modules=['declic'],
    url='https://github.com/Septaris/declic',
    license='MIT',
    author='S. Lion',
    author_email='sonny.lion@laposte.net',
    description='Declic (DEcorator-oriented CLI Creator) is a tiny Python 3 package for creating command line interfaces',
    long_description=long_description,
    long_description_content_type='text/x-rst'
)
