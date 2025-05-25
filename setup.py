from setuptools import setup, find_packages

setup(
    name='visuscript',  # Replace with the actual name of your package
    version='0.1.0',          # Initial version number
    packages=find_packages(),   # Automatically discover your package(s)
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