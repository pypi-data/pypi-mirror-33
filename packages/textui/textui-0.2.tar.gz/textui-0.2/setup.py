from setuptools import setup

# List of classifiers: https://pypi.org/pypi?%3Aaction=list_classifiers
with open("README.md", "r") as fh:
    long_description = fh.read()

versionstr = '0.2'
setup(
    name='textui',
    packages=['textui'], # this must be the same as the name above for PyPI
    version=versionstr,
    description='A text-based UI system',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Josh Laughner (firsttempora)',
    author_email='first.tempora@gmail.com',
    url='https://github.com/firsttempora/Python-textui', # use the URL to the github repo
    download_url='https://github.com/firsttempora/Python-textui/tarball/{0}'.format(versionstr), # version must be a git tag
    keywords=['UI', 'user interface', 'text-based'],
    classifiers=['License :: OSI Approved :: MIT License'],
    install_requires=['backports.shutil_get_terminal_size'],
)