import setuptools
from setuptools import find_packages

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)

setuptools.setup(
    name='dashbase_tools',
    version='2.0.0',
    url='http://www.dashbase.io',
    maintainer='khou',
    maintainer_email='kevin@dashbase.io',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    install_requires=requirements,
    setup_requires=test_requirements,
    entry_points='''
        [console_scripts]
        dash=tools.dbsql:main
        dtail=tools.dtail:main
    ''',
)
