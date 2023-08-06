import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cjs_fdc",
    version="0.0.2b1",
    author="CJS",
    author_email="0empcjs@gmail.com",
    description="count the number of files or dirs in a given dir",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CCC-S/cjs_fdc",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    classifiers=(
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ),
    entry_points='''
        [console_scripts]
        cjs_fdc=cjs_fdc.cjs_fdc:fdc
    ''',
)
