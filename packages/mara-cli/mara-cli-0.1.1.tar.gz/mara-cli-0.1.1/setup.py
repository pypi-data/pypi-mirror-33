from setuptools import setup, find_packages

def get_long_description():
    with open('README.md') as f:
        return f.read()

setup(
    name='mara-cli',
    version='0.1.1',

    description="Mara cli app which calls the appropriate contributed subcommand.",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',

    install_requires=[
        'mara-config>=0.1.4',
        'click'
        ],

    dependency_links=[
        'git+https://github.com/mara/mara-config.git@master#egg=mara-config',
    ],

    extras_require={
        'test': ['pytest', 'pytest_click'],
    },

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={
        'console_scripts': [
            'mara = mara_cli.cli:main',
        ],
    },

)
