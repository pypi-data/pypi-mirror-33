from setuptools import setup

with open('./dguslib/version.py') as fd:
    exec(fd.read())

with open('README.md') as fd:
    long_description = fd.read()

setup(
    name='trimarlib-dgus',
    version=VERSION,
    author='Kacper Kubkowski',
    author_email='k.kubkowski@trimar.com.pl',
    description='DWIN DGUS display utility library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://dsl2.trimar.org/pythons/dguslib',
    packages=[
        'dguslib',
        'dguslib.configuration'
        ],
    install_requires=[
        'pyserial',
        'webcolors',
        'crcmod'
        ],
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Embedded Systems'
        ),
    )
