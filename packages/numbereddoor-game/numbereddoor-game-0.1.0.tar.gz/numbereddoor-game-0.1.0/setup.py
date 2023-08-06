import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='numbereddoor-game',
    version='0.1.0',
    author='Coul Greer',
    author_email='coulgreer1@hotmail.com',
    description='A recreation of the door puzzles from the Nonary game, 999.',
    long_description=long_description,
    url='https://github.com/cagreer18/NumberedDoorGame',
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=(
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent'
    )
)
