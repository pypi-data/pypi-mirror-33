import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

version = "1.0.2"

setuptools.setup(
    name="seagen",
    packages=setuptools.find_packages(),
    version="%s" % version,
    description="Stretched Equal Area Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jacob Kegerreis",
    author_email="jacob.kegerreis@durham.ac.uk",
    url="https://github.com/jkeger/seagen",
    download_url="https://github.com/jkeger/seagen/archive/%s.tar.gz" % version,
    license="GNU GPLv3+",
    py_modules=["seagen"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Development Status :: 4 - Beta",
        ],
    python_requires=">=2",
    keywords=["particle arrangement density sphere shell SPH"],
)
