import os

from setuptools import setup, find_packages

basepath = os.path.dirname(__file__)


with open('README.rst') as file:
    long_description = file.read()


def main():
    install_reqs = ['Flask==1.0.2',
                    'flask-login==0.4.1',
                    'flask-sqlalchemy==2.3.1',
                    'flask-wtf==0.14.2',
                    'passlib==1.7.1',
                    'taskw==1.2.0']

    setup(name='twweb',
          description='Taskwarrior Web View',
          long_description=long_description,
          use_scm_version={'write_to': '.version.txt'},
          license='GPLv3+',
          author='Michał Góral',
          author_email='dev@mgoral.org',
          url='',
          platforms=['linux'],
          setup_requires=['setuptools_scm', 'babel'],
          install_requires=install_reqs,

          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=['Development Status :: 3 - Alpha',
                       'Environment :: Web Environment',
                       'Framework :: Flask',
                       'Intended Audience :: Developers',
                       'Intended Audience :: System Administrators',
                       'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python :: 3 :: Only',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: 3.6',
                       'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                       'Topic :: Utilities'],

          packages=find_packages('src'),
          package_dir={'': 'src'},
          include_package_data=True,
    )


if __name__ == '__main__':
    main()
