from setuptools import setup, find_packages
import os
import pelops


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if os.path.isfile(os.path.join(os.path.dirname(__file__), 'README_SUPPORT.md')):
    from pypandoc import convert
    readme_rst = convert(os.path.join(os.path.dirname(__file__), 'README_SUPPORT.md'), 'rst')
    with open(os.path.join(os.path.dirname(__file__), 'README_SUPPORT.rst'), 'w') as out:
        out.write(readme_rst + '\n')

setup(
    name='Pelops',
    version=pelops.version,
    packages=find_packages(),
    license='MIT license',
    long_description=read('README_SUPPORT.rst'),
    description='Common tools for projects of the the gitlab group pelops.',
    url='https://gitlab.com/pelops/pelops/',
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
    data_files=[('.', ['README_SUPPORT.rst']),
                ],
    python_requires='>=3.5',
    install_requires=[
        "paho-mqtt",
        "pyyaml",
        "jsonschema",
    ],
    test_suite="tests",
)
