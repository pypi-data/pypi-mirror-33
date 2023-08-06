from setuptools import setup, find_packages
import run

setup(
    name="add_gitignore",
    version="0.1.0",
    author="fanny vieira",
    author_email="fannyvieira082@gmail.com",
    packages=find_packages(),
    url="https://github.com/pypa/example-project",
    entry_points={
        'console_scripts': [
            'add-gitignore = run:command_line_runner',
        ]
    },
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    description="A small example package"
)