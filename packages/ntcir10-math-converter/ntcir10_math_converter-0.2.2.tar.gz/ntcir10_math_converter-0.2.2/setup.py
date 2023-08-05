from os import path
from setuptools import setup, find_packages

AUTHOR = "Vit Novotny"
HERE = path.abspath(path.dirname(__file__))
SOURCE_URL = "https://github.com/MIR-MU/ntcir10-math-converter"

# Get the long description from the README file
with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


setup(
    author=AUTHOR,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    description="""
        The NTCIR-10 Math Converter package converts NTCIR-10 Math XHTML dataset and relevance
        judgements to the NTCIR-11 Math-2, and NTCIR-12 MathIR XHTML5 format.
    """,
    entry_points={
        'console_scripts': [
            'ntcir10-math-converter=ntcir10_math_converter.__main__:main',
        ],
    },
    keywords="ntcir math_information_retrieval",
    install_requires=[
        "beautifulsoup4 ~= 4.6.0",
        "lxml ~= 4.2.1",
        "tqdm ~= 4.23.3",
    ],
    license="MIT",
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    maintainer=AUTHOR,
    name="ntcir10_math_converter",
    packages=find_packages(),
    python_requires="~= 3.4",
    project_urls={
        "Source": SOURCE_URL,
    },
    url=SOURCE_URL,
    version="0.2.2",
)
