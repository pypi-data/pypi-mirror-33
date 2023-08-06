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
    install_requires=[],
    extras_require={
        'dev': [
            'flake8',
            'pytest',
            'sphinx',
        ],
    },
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
