import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='refclone',
    version='0.1',
    url='https://bitbucket.org/alcm-b/refclone',
    author='Egor Berdnikov',
    author_email='egor.berdnikov@gmail.com',
    license='MIT',
    description='A wrapper for "git clone" that keeps git repo directories organized',
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=['POSIX'],
    entry_points=dict(
        console_scripts=['refclone = refclone:run']
    ),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    packages=['refclone'],
    classifiers=(
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
