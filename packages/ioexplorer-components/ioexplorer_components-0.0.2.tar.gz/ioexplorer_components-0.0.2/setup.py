from setuptools import setup

exec (open('ioexplorer_components/version.py').read())

setup(
    name='ioexplorer_components',
    version=__version__,
    author='rmarren1',
    packages=['ioexplorer_components'],
    include_package_data=True,
    license='MIT',
    description='Components for the IOExplorer Web App',
    install_requires=[]
)
