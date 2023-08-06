from setuptools import setup, find_packages

setup(
    name='eggit',
    version='0.0.7',
    description='a python lib',
    author='JoiT',
    author_email='myjoit@outlook.com',
    url='https://github.com/MyJoiT/eggit',
    download_url='https://github.com/MyJoiT/eggit/archive/0.0.7.tar.gz',
    packages=find_packages(exclude=[]),
    keywords=('eggit, lib, tool'),
    install_requires=[
        'pyjwt>=1.4.2',
        'sqlalchemy>=1.2.7'
        ],
    license='GPL3',
    zip_safe=True
)
