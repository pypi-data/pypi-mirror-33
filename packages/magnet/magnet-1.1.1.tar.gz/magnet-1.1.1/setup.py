import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='magnet',
    version='1.1.1',
    author='Jerko Steiner',
    author_email='jerko.steiner@gmail.com',
    description=(
        'Hierarchical YAML config reader that reads from multiple files and'
        ' an environment variable'
    ),
    install_requires=[
        'PyYAML>=3.12'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/jeremija/pymagnet',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
