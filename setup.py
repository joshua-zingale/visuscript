from setuptools import setup, find_packages
import os
def get_dependencies():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    requirements_path = os.path.join(dir_path, 'requirements.txt')
    with open(requirements_path, "r") as f:
        dependencies = list(filter(lambda x: len(x) > 0 and not x.startswith("#"), map(lambda x: x.strip(), f.readlines())))
    return dependencies

setup(
    name='visuscript',
    version='0.1.0',
    packages=find_packages(),
    install_requires=get_dependencies(),
    entry_points={
        'console_scripts': [
            'visuscript = visuscript.cli.visuscript_cli:main',
        ],
    },
    scripts=[
        'scripts/visuscript-animate',
        'scripts/visuscript-slideshow'
    ],
    include_package_data=True,
    package_data={
        'visuscript': [
            'fonts/Arimo/*',
            'fonts/LeagueMono-2.300/*',
        ],
    },
)