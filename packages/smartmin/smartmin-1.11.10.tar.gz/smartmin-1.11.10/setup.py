from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def _is_requirement(line):
    """Returns whether the line is a valid package requirement."""
    line = line.strip()
    return line and not line.startswith("#")


def _read_requirements(filename):
    """Parses a file for pip installation requirements."""
    with open(filename) as requirements_file:
        contents = requirements_file.read()
    return [line.strip() for line in contents.splitlines() if _is_requirement(line)]


setup(
    name='smartmin',
    version=__import__('smartmin').__version__,
    description="Scaffolding system for Django object management.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Nyaruka Ltd',
    author_email='code@nyaruka.com',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    keywords='django scaffolding crudl',
    url='http://github.com/nyaruka/smartmin',
    license="BSD",

    packages=find_packages(),
    install_requires=_read_requirements("requirements/base.txt"),
    tests_require=_read_requirements("requirements/tests.txt"),

    include_package_data=True,
    zip_safe=False
)
