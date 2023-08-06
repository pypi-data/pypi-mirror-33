import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='webpageshot',
    version='0.2',
    description='take screenshot of webpage ',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Zhongqiang Shen',
    author_email='shenzhongqiang@msn.com',
    url='https://github.com/pythonml/webpageshot',
    packages=setuptools.find_packages(),
    install_requires=['selenium>=3.12.0'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'webpageshot=webpageshot:main'
        ],
    },
)
