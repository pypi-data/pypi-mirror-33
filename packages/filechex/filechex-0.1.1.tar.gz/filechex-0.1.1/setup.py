import setuptools

setuptools.setup(
    name="filechex",
    version="0.1.1",
    url="https://github.com/cw-andrews/cookiecutter-pypackage-minimal",

    author="cw-andrews",
    author_email="cwandrews.oh@gmail.com",

    description=("A utility package designed to compare files to determine "
                 "whether source files should be processed."),
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)
