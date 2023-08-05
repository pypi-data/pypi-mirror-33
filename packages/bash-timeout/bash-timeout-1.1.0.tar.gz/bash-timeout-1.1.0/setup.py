from setuptools import setup
setup(
    name='bash-timeout',
    version='1.1.0',
    description='A command (and also bash function) to terminate another command after specified duration',
    long_description='bash-timeout is a command and also a bash function in order to terminate the target command if the target command does not finish within the duration specified beforehand.  The input via either redirection ( < FILE ) or pipe ( | ) are transferred to the target command transparently. The exit status of the target command is retained if the target command finishes within the duration.',
    url='https://github.com/nogayama/bash-timeout',
    author='Takahide Nogayama',
    author_email='nogayama@gmail.com',
    license='MIT',
    zip_safe=False,
    scripts=[
        'bin/bash-timeout',
    ],
   classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Unix Shell',
        'Topic :: System :: Shells',
        'Topic :: Utilities'
    ],
)