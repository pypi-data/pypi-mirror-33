import os
import codecs
import versioneer
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    name='txdocumint',
    description='Twisted Python clj-documint client implementation',
    license='MIT',
    url='https://github.com/fusionapp/txdocumint',
    author='Jonathan Jacobs',
    author_email='jonathan@jsphere.com',
    maintainer='Jonathan Jacobs',
    maintainer_email='jonathan@jsphere.com',
    include_package_data=True,
    long_description=read('README.rst'),
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Twisted[tls]>=15.5.0',
        'treq>=15.1.0',
    ],
    extras_require={
        'test': ['pytest>=2.7.1', 'testtools>=2.0.0'],
    },
)
