from distutils.core import setup

VERSION = '0.1.0'
desc    = """Command-line interface extends python's cmd.Cmd utiling the hoomanlogic text-based human language input framework."""

setup(name='hoomancmd',
        version=VERSION, 
        author='Geoffrey Floyd',
        author_email='geoffrey.floyd@hoomanlogic.com',
        url='http://github.com/hoomanlogic/hoomancmd/',
        download_url='https://pypi.python.org/pypi/hoomancmd/',
        description="Command-line interface extends python's cmd.Cmd utiling the hoomanlogic text-based human language input framework.",
        license='http://www.apache.org/licenses/LICENSE-2.0',
        packages=['hoomancmd'],
        platforms=['Any'],
        long_description=desc,
        classifiers=['Development Status :: 4 - Beta',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Apache Software License',
                     'Operating System :: OS Independent',
                     'Topic :: Text Processing',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7'
                    ]
        )