from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

exec(open('tubedreams/version.py').read())

setup(
    name='tubedreams',
    version=__version__,
    description='create dream-sequences from your video browsing history',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hdbhdb/tubedreams",
    author='Hudson Bailey',
    author_email='hudsondiggsbailey@gmail.com',
    license='MIT',
    packages=['tubedreams'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'sox>=1.3.3',
        'youtube_dl>=2018.5.18',
        'ez_setup>=0.9',
        'moviepy>=0.2.3.5',
        'ffmpy>=0.2.2',
    ],
    scripts=['bin/tubedreams'],
    zip_safe=False)
