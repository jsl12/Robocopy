from setuptools import setup, find_packages

setup(
    name='robocopy',
    version='1.0',
    description='Pure Python wrapper for the Windows robocopy function',
    packages=find_packages(),
    entry_points={"console_scripts": ["robocopy-yaml=robocopy:robocopy_yaml"]}
)