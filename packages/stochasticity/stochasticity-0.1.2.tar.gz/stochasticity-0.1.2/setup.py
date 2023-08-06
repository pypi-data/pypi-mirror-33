from setuptools import setup

setup(
    name='stochasticity',
    version='0.1.2',
    packages=['coin', 'coin.test'],
    url='https://github.com/jeffwhite-619/stochasticity',
    license='GNU GPLv3',
    author='Jeff White',
    author_email='thisguy@thejeffwhite.com',
    description='Modules to generate various sorts of randomness, starting with a simple coin flip',
    long_description=open('README.txt').read()
)
