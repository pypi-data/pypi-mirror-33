import codecs
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


install_requires = [
    'molo.core>=6.0.0, <=7.0.0'
]

setup(name='molo.usermetadata',
      version=read('VERSION'),
      description=('User metadata to be used with Molo.'),
      long_description=read('README.rst'),
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Django",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Praekelt.org',
      author_email='dev@praekelt.org',
      url='http://github.com/praekelt/molo.usermetadata',
      license='BSD',
      keywords='praekelt, mobi, web, django',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['molo'],
      install_requires=install_requires,
      extras_require = {
        'test': [
            'pytest==3.0.0',
            'pytest-django==3.1.1',
            'responses',
        ],
        'cover': [
            'pytest-cov',
        ],
        'lint': [
            'flake8==3.4.1',
        ],
      },
      entry_points={})
