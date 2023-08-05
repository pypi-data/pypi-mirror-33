from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='motherjokes',
    version='0.1',
    description='Transform sentences into awesome jokes about your mother (in russian language for now)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/FFFEGO/motherjokes',
    author='Vladimir Kaigorodov',
    author_email='vladimir.kgrdv@gmail.com',
    packages=['motherjokes'],
    install_requires=[
        'pymorphy2==0.8',
        'mosestokenizer==1.0.0',
    ],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing :: Linguistic',
    ),
    license='MIT',
)
