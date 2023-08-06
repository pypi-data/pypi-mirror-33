from setuptools import setup

setup(name='ntr',
      version='0.0.3',
      description='A Python 3+ CLI application for note.txt notes',
      long_description=open('README.rst').read(),
      url='http://github.com/mrshu/py-ntr',
      author='Marek Suppa (mr.Shu)',
      author_email='mr@shu.io',
      license='MIT',
      py_modules=['ntr'],
      install_requires=[
        'Click',
        'arrow',
        'notetxt'
      ],
      entry_points='''
        [console_scripts]
        ntr=ntr:ntr
      ''',
      zip_safe=False)
