from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='pascalvoc_to_image',
    version='1.0.0',
    url='http://www.gitlab.com/jdreg95/pascalvoc-to-image',
    author='Jori Regter',
    author_email='joriregter@gmail.com',
    description='Tool to cut images from bounding boxes in PascalVOC XML files.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='GNU GPLv3',
    packages=find_packages(),
    scripts=['bin/pascalvoc-to-image'],
    install_requires=install_requires
)
