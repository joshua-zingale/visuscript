from setuptools import setup, find_packages

setup(
    name='visuscript',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'visuscript = visuscript.cli.visuscript_cli:main',
        ],
    },
    scripts=[
        'scripts/visuscript-animate',
        'scripts/visuscript-slideshow'
    ],
)