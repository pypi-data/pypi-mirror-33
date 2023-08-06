from setuptools import setup, find_packages


def README() -> str:
    """Return the contents of the README file for this project."""
    with open('README.md') as README_file:
        return README_file.read()


setup(
    name='nes_py',
    setup_requires=[
        'very-good-setuptools-git-version'
    ],
    version_format='{tag}',
    description='An NES Emulator for Python3 clients',
    long_description=README(),
    long_description_content_type='text/markdown',
    keywords='NES Emulator',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Emulators',
    ],
    url='https://github.com/Kautenja/nes-py',
    author='Christian Kauten',
    author_email='kautencreations@gmail.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    # install_requires=[
    #     'gym>=0.10.5',
    #     'numpy>=1.14.2',
    # ],
    entry_points={
        'console_scripts': [
            'nes_py = nes_py._app.cli:main',
        ],
    },
)
