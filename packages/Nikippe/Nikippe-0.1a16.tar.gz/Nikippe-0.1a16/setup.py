from setuptools import setup, find_packages
import os
import nikippe


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if os.path.isfile(os.path.join(os.path.dirname(__file__), 'README.md')):
    from pypandoc import convert
    readme_rst = convert(os.path.join(os.path.dirname(__file__), 'README.md'), 'rst')
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'w') as out:
        out.write(readme_rst + '\n')

setup(
    name='Nikippe',
    version=nikippe.version,
    packages=find_packages(),
    license='MIT license',
    long_description=read('README.rst'),
    description='A general purpose display server - takes values from mqtt and publishes the resulting image to mqtt.',
    url='https://gitlab.com/pelops/nikippe/',
    author='Tobias Gawron-Deutsch',
    author_email='tobias@strix.at',
    keywords='mqtt device driver rpi raspberry pi',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.5',
    install_requires=[
        "pelops>=0.1a25",
        "PIL",
    ],
    entry_points={
        'console_scripts': [
            'nikippe = nikippe.displayserver:standalone',
        ]
    },
)
