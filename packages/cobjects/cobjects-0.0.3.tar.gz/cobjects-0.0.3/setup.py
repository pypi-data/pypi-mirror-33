from setuptools import setup



setup(
        name='cobjects',
        version='0.0.3',
        description='Manage C data from Python for C libraries',
        author='Riccardo De Maria',
        author_email='riccardo.de.maria@cern.ch',
        url='https://github.com/rdemaria/cobjects',
        python_requires='>=3.6',
        packages=['cobjects'],
        package_dir={'cobjects': 'cobjects'},
        cffi_modules=["_cffi_build/cbuffer_builder.py:ffibuilder"],
        install_requires=['numpy','cffi>=1.0.0'],
        setup_requires=['cffi>=1.0.0']
)


