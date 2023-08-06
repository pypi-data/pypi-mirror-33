from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='ranking_table_tennis',
      version='2017.3',
      description='A ranking table tennis system',
      url='http://github.com/srvanrell/ranking-table-tennis',
      author='Sebastian Vanrell',
      author_email='srvanrell@gmail.com',
      license='MIT',
      packages=['ranking_table_tennis'],
      scripts=['bin/preprocess.py',
               'bin/compute_rankings.py',
               'bin/publish.py'],
      include_package_data=True,
      install_requires=[
          'gspread==3.0.0',
          'oauth2client==4.1.2',
          'PyYAML==3.12',
          'urllib3==1.22',
          'openpyxl==2.4.2',
      ],
      zip_safe=False)
