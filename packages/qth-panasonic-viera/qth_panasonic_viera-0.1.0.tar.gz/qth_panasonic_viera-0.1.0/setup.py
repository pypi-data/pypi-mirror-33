from setuptools import setup, find_packages

with open("qth_panasonic_viera/version.py", "r") as f:
    exec(f.read())

setup(
    name="qth_panasonic_viera",
    version=__version__,
    packages=find_packages(),

    # Metadata for PyPi
    url="https://github.com/mossblaser/qth_panasonic_viera",
    author="Jonathan Heathcote",
    description="A minimal Qth interface for controlling Panasonic VIERA TVs.",
    license="GPLv2",
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",

        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="home-automation panasonic viera tv",

    # Requirements
    install_requires=["qth>=0.6.0", "panasonic-viera>=0.3.1"],

    # Scripts
    entry_points={
        "console_scripts": [
            "qth_panasonic_viera = qth_panasonic_viera:main",
        ],
    }
)
