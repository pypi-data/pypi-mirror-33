from setuptools import setup
from getcomic import version

dependencies=['fpdf','selenium','pathlib']

with open("README.md",'r') as f:
    long_description=f.read()

setup(
        name='getcomic',
        description='A command line tool to download comics from readcomiconline.to',
        url='https://github.com/VinitraMk/getcomic-cli',
        author='VinitraMk',
        author_email='vinitramk@gmail.com',
        packages=[
            'getcomic'
        ],
        version=version,
        install_requires=dependencies,
        entry_points={
            'console_scripts':[
                'getcomic=getcomic.getcomic:main',
            ],
        },
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Operating System :: POSIX',
            'Programming Language :: Python',
        ],
    )
