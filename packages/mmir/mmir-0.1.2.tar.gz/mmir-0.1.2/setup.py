import setuptools

with open("README.md") as fh:
    long_description = fh.read()


setuptools.setup(
    name="mmir",
    version="0.1.2",
    author="Alexandru Kis",
    author_email="alexandrukis1618033@gmail.com",
    description="A package for helping you register VIS and LWIR images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/_alexandrukis/pyreg/src/master/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'bresenham==0.2',
        'dataclasses==0.6',
        'funcy==1.10.2',
        'joblib==0.12.0',
        'multipledispatch==0.5.0',
        'numpy==1.14.5',
        'opencv-contrib-python==3.4.1.15',
        'scikit-image==0.14.0',
        'scipy==1.1.0',
    ]
)
