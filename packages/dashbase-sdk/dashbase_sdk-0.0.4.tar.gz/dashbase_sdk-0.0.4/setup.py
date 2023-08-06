import setuptools
from setuptools import find_packages

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)

setuptools.setup(
    name="dashbase_sdk",
    version="0.0.4",
    author="peter wang",
    author_email="peter@dashbase.io",
    description="Dashbase python sdk",
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    setup_requires=test_requirements,
    install_requires=requirements
)
