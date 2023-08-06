import os

from setuptools import setup, find_packages

import agiletoolkit as pkg


def read(name):
    filename = os.path.join(os.path.dirname(__file__), name)
    with open(filename) as fp:
        return fp.read()


def requirements(name):
    install_requires = []
    dependency_links = []

    for line in read(name).split('\n'):
        if line.startswith('-e '):
            link = line[3:].strip()
            if link == '.':
                continue
            dependency_links.append(link)
            line = link.split('=')[1]
        line = line.strip()
        if line:
            install_requires.append(line)

    return install_requires, dependency_links


meta = dict(
    version=pkg.__version__,
    description=pkg.__doc__,
    name='agile-toolkit',
    author='Luca Sbardella',
    author_email="luca@lendingblock.com",
    maintainer_email="luca@lendingblock.com",
    url="https://github.com/lendingblock/agile-toolkit",
    long_description=read('readme.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements('dev/requirements.txt')[0],
    entry_points={
        "console_scripts": [
            "agilekit=agiletoolkit.commands:start"
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities'
    ]
)


if __name__ == '__main__':
    setup(**meta)
