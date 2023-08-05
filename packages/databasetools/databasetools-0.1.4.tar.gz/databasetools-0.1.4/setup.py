from setuptools import setup, find_packages

setup(
    name='databasetools',
    version='0.1.4',
    packages=find_packages(),
    install_requires=[
              'certifi==2018.4.16',
              'chardet==3.0.4',
              'entrypoints==0.2.3',
              'ez-setup==0.9',
              'idna==2.7',
              'looptools',
              'mysql-connector==2.1.6',
              'numpy==1.14.5',
              'pandas==0.23.1',
              'pkginfo==1.4.2',
              'python-dateutil==2.7.3',
              'pytz==2018.4',
              'requests==2.19.1',
              'requests-toolbelt==0.8.0',
              'six==1.11.0',
              'tqdm==4.23.4',
              'twine==1.11.0',
              'urllib3==1.23',
          ],
    url='https://github.com/mrstephenneal/databasetools.git',
    license='MIT License',
    author='Stephen Neal',
    author_email='stephen@stephenneal.net',
    description='A collection of database tools written in Python for handling basic actions with CSV files, '
                'numpy dictionarie, SQLite databases and MySQL databases.'
)
