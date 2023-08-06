import setuptools

setuptools.setup(
    name="comet_ml",
    packages=["comet_ml"],
    version="1.0.17",
    url="https://www.comet.ml",
    author="Comet ML Inc.",
    author_email="mail@comet.ml",
    description="Supercharging Machine Learning",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    install_requires=[
        "websocket-client>=0.44.0",
        "requests>=2.18.4",
        "six",
        "wurlitzer>=1.0.2",
        "netifaces>=0.10.7",
    ],
    include_package_data=True,
    test_requires=["websocket-server", "pytest", "responses"],
    scripts=["comet_ml/scripts/jupyter-comet_ml"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
