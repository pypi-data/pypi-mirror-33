from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='indicatorcalc',
    version='0.1a30',
    author='Hunter M. Allen',
    author_email='allenhm@gmail.com',
    license='MIT',
    #packages=find_packages(),
    packages=['indicatorcalc',
              'indicatorcalc_redux'],
    #scripts=['bin/heartbeatmonitor.py'],
    install_requires=['numpy',
                      'TA-Lib'],
    description='Centralized, TA-Lib based technical analysis indicator calculation from json market data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hmallen/indicatorcalc',
    keywords=['indicator', 'calc'],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
