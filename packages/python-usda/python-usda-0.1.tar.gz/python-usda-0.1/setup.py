from setuptools import setup, find_packages


def read_requirements(filename):
    return [req.strip() for req in open(filename)]


setup(
    name='python-usda',
    version='0.1',
    author='Lucidiot',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={
        '': ['*.md', 'LICENSE', 'README'],
    },
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
    },
    license='GNU General Public License 3',
    description="A fork of pygov focused on USDA nutritional database API",
    long_description=open('README.md').read(),
    keywords="api usda nutrition food",
    url="https://github.com/Lucidiot/python-usda",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
    project_urls={
        "Source Code": "https://github.com/Lucidiot/python-usda",
        "Gitter Chat": "https://gitter.im/BrainshitPseudoScience/Lobby",
    }
)
