from setuptools import setup

setup(name='dsk2obj',
    version='0.5',
    description='generates an obj file from a bds file (dsk kernel) and dsiplays it',
    author='Alfredo Escalante',
    author_email='alfredoescalante95@gmail.com',
    # license='GPL',
    packages=['dsk2obj'],
    install_requires=['spiceypy','numpy','pygame'],
    python_requires='>=3',
)