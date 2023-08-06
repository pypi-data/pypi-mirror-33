import io
from os.path import abspath, dirname, join
from setuptools import setup, find_packages

HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.rst'
])

setup(name='workonflow-bot-client',
      version='0.0.2',
      description='python bot-client for workonflow',
      long_description=DESCRIPTION,
      classifiers=[ 'License :: OSI Approved :: MIT License', 'Programming Language :: Python :: 3.6' ],
      keywords='bot-client bot workonflow',
      # url='http://github.com/storborg/funniest',
      author='Akbashev Rustam',
      author_email='402@onlinepbx.ru',
      license='MIT',
      packages=find_packages(),
      install_requires=[ 'socketIO_client_nexus>=0.7.6', ],
      include_package_data=True,
      zip_safe=False)
