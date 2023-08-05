from setuptools import find_packages, setup

setup(
    name="ereuse-utils",
    version='0.3.0b2',
    packages=find_packages(),
    url='https://github.com/eReuse/utils',
    license='AGPLv3 License',
    author='eReuse.org team',
    author_email='x.bustamante@ereuse.org',
    description='Common functionality for eReuse.org software',
    install_requires=[
        'boltons'
    ],
    extras_require={
        'naming': ['inflection'],
        'usb_flash_drive': ['pyusb', 'inflection'],  # Check pyusb requirements
        'test': ['flask']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Logging',
        'Topic :: Utilities',
    ],
)
