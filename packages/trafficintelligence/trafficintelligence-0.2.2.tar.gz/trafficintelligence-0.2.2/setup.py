import setuptools

with open('README') as file:
    long_description = file.read()

setuptools.setup(
    name='trafficintelligence',
    version='0.2.2',
    description='Python modules of the Traffic Intelligence project',
    author='Nicolas Saunier',
    author_email='nicolas.saunier@polymtl.ca',
    url='https://bitbucket.org/Nicolas/trafficintelligence',
    packages=setuptools.find_packages(),
    long_description=long_description,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
