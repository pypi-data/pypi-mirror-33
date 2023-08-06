from setuptools import setup

# SEE: `https://packaging.python.org/tutorials/distributing-packages/#setup-args`
# And SEE: `https://python-packaging.readthedocs.io/en/latest/minimal.html`.
setup(
    name="beam-io-utils",
    version="0.0.5",
    description="Utilities for Apache Beam disk io (local or on GCP)",
    url="https://github.com/raywhite/beam-io-utils",
    author="axdg",
    author_email="axdg@dfant.asia",
    license="UNLICENSED",
    classifiers=[],
    keywords="apache beam dataflow google cloud platform",
    packages=["beam_io_utils"],
    install_requires=["apache-beam[gcp]"],
    python_requires=">=2.6,<=3.0",
    package_date={},
    data_files=[],
    py_modules=[],
    entry_points={},
    console_scripts={},
    scripts=[])
