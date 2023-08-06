import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fftpower23",
    version="1.0.0",
    author="Vladimir Popov",
    author_email="vladimir.popov@gmx.com",
    description="Fast Fourier Transformation with powers 2 and 3",
    long_description=long_description,
    url="https://bitbucket.org/VladimirPopov43/fft_python/src",
    py_modules=['fftpower23'],
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ),
)
