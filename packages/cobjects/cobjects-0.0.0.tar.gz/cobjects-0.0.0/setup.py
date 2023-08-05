import setuptools

setuptools.setup(
        name='cobjects',
        version='0.0.0',
        description='Manage C data from Python for C libraries',
        author='Riccardo De Maria',
        author_email='riccardo.de.maria@cern.ch',
        url='https://github.com/rdemaria/cobjects',
        packages=['cobjects'],
        package_dir={'cobjects': 'cobjects'},
        install_requires=['numpy','cffi']
)


