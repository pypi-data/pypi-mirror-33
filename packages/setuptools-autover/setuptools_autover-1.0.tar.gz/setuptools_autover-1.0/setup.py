import setuptools

import setuptools_autover


setuptools.setup(
    name="setuptools_autover",
    version=setuptools_autover.get_version(),
    description='Automatic package version numbering from version control',
    url='https://github.com/jannero/setuptools_autover',
    author='Janne Rönkkö',
    author_email='jroo@iki.fi',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Archiving :: Packaging',
    ],
    keywords='setuptools development git version',
    packages=['setuptools_autover'],
    python_requires='>=3.4',
    entry_points={
        'distutils.setup_keywords': [
            'version = setuptools_autover.autover:handle_version',
            'use_autover = setuptools_autover.autover:handle_use_autover',
        ],
    },
)
