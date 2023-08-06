from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

install_requires = []
with open('requirements.txt', mode='r') as requirements_file:
    for line in requirements_file.readlines():
        if line and not line.startswith('#'):
            install_requires.append(line)

packages = find_packages()

setup(
    name='arst',
    version='1.0.1',
    description='Poor man\'s yo generator.',
    long_description = readme,
    author='Bogdan Mustiata',
    author_email='bogdan.mustiata@gmail.com',
    license='BSD',
    entry_points = {
        "console_scripts": [
            "ars = arst.launcher:launch",
            "arst = arst.launcher:launch"
        ]
    },
	install_requires=install_requires,
	packages=packages,
    package_data={
        '': ['*.txt', '*.rst']
    })
