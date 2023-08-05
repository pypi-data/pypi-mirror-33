from setuptools import setup

with open('./apsbblib/version.py') as fd:
    exec(fd.read())

with open('README.md') as fd:
    long_description = fd.read()

setup(
    name='trimarlib-apsbb',
    version=VERSION,
    author='Kacper Kubkowski',
    author_email='k.kubkowski@trimar.com.pl',
    description='APS Backbone Python wrapper for Linux host',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://dsl2.trimar.org/pythons/apsbblib',
    packages=[
        'apsbblib',
        'apsbblib.device_service',
        'apsbblib.device_service.apsbb',
        'apsbblib.system_service',
        'apsbblib.system_service.apsbbsys'
        ],
    install_requires=[
        'pyserial',
        'erpc==1.6',
        'trimarlib-sysfsgpio'
        ],
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: System :: Hardware :: Hardware Drivers'
        ),
    )
