from setuptools import setup

setup(name='tle2spk',
    version='0.4',
    description='Convert from Two Line Elements to binary .spk kernel',
    author='Alfredo Escalante',
    author_email='alfredoescalante95@gmail.com',
    # license='GPL',
    packages=['tle2spk'],
    install_requires=['spiceypy','numpy'],
    python_requires='>=3',
)