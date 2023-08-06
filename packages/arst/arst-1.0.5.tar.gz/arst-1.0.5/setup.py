from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

packages = find_packages()

setup(
    name='arst',
    version='1.0.5',
    description='Poor man\'s yo generator.',
    long_description=readme,
    author='Bogdan Mustiata',
    author_email='bogdan.mustiata@gmail.com',
    license='BSD',
    entry_points={
        "console_scripts": [
            "ars = arst.launcher:launch",
            "arst = arst.launcher:launch"
        ]
    },
    install_requires=["pybars3==0.9.3", "termcolor==1.1.0", "colorama==0.3.9", "mdvl==2017.7.16.7", "PyYAML==3.12"],
    packages=packages,
    package_data={
        '': ['*.txt', '*.rst']
    }
)
