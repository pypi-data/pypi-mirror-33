
from setuptools import setup


__version__ = "1.0.1"


setup(
    name="simple-pinq",
    version=__version__,
    url="https://github.com/tizz98/pinq",
    download_url="https://github.com/tizz98/pinq/tarball/{version}".format(
        version=__version__,
    ),
    author="Elijah Wilson",
    author_email="elijah@elijahwilson.me",
    description="LINQ style API for Python.",
    long_description=open('README.md').read(),
    license="MIT",
    keywords="linq pinq api",
    install_requires=[],
    packages=[
        "pinq",
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe=True,
)
