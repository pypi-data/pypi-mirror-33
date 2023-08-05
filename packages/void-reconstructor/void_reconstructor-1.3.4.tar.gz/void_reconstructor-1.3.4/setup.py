from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()



setup(
    name='void_reconstructor',    # This is the name of your PyPI-package.
    description='Tools for reconstructing the velocities in a LCDM universe using the Jonker-Volgenant algorithm',
    long_description=readme(),
    version='1.3.4',# Update the version number for new releases
    author_email = 'tobias.meier@epfl.ch',
    install_requires=['lapjv','astropy'],
    packages=['void_reconstructor'],         # The name of your scipt, and also the command you'll be using for calling it
    python_requires='>=3'
    )
