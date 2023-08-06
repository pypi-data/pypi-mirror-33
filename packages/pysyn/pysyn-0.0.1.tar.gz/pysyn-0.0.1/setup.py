import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='pysyn',
    version='0.0.1',
    author='Victor De Gouveia',
    author_email='vdegou@gmail.com',
    description='Password management and data synchronization app',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://0xacab.org/vdegou/Syn",
    packages=setuptools.find_packages(),
    py_modules=['data', 'generator', 'registration', 'syn', 'syn_utils', '__init__'],
    install_requires=[
        'Click',
        'leap.common',
        'leap.soledad',
        'pytest',
        'zope.proxy', # This is an indirect dependency from Soledad's adbapi.py
        'pysqlcipher', # This is an indirect dependency from Soledad
        'tornado', # Same as above
    ],
    entry_points='''
        [console_scripts]
        syn=syn:cli
    ''',
)
