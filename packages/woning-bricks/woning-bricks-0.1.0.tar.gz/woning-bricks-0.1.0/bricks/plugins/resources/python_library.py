setup_py_template = """
from setuptools import setup, find_packages

setup(
    name="{project.metadata.name}",
    description="{project.metadata.description}",
    version="{project.metadata.version}",
    packages=find_packages(),
    install_requires=[
        # add the install dependencies here
    ]
)
""".lstrip()

requirements_dev = """
-e .
pytest
twine
""".lstrip()

bumpversion_cfg = """
[bumpversion]
current_version = {project.metadata.version}
tag = True
commit = True

[bumpversion:file:setup.py]

[bumpversion:file:bricks.yml]

""".lstrip()

default_test_py = """
def test_default():
    assert True
"""
