import ast

from setuptools import setup, find_packages


with open('.project_metadata.py') as meta_file:
    project_metadata = ast.literal_eval(meta_file.read())


with open('README.rst') as readme_file:
    long_description = readme_file.read()
    long_description_content_type = 'text/x-rst'


setup(
    name=project_metadata['name'],
    version=project_metadata['release'],
    author=project_metadata['author'],
    author_email=project_metadata['author_email'],
    description=project_metadata['description'],
    url=project_metadata['url'],
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    license=project_metadata['license'],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    install_requires=[
        'click',
    ],
    extras_require={
        'dev': [
            'flake8',
            'pytest',
            'sphinx',
            'sphinx-view',
        ],
    },
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'weighted-choice = weighted_choice.cli:main',
        ],
    },
)
