from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='Yuci Dictionary',
    version='0.1.5',
    package=find_packages(),
    description='A tiny CLI dictionary built by python, based on youdao-web dictionary and require an internet connection.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='python youdao terminal',
    py_modules=['dictionary.youdao_dict', 'dictionary.error_handler', 'dictionary.history'],
    author='Yucklys',
    author_email='yucklys687@outlook.com',
    url='https://github.com/Yucklys/yuci-dictionary',
    license='MIT',
    include_package_data=True,
    install_requires=[
        'beautifulsoup4>=4.6.0',
        'lxml>=4.0.0'
    ],
    entry_points={
        'console_scripts': [
            'dict = dictionary.youdao_dict:main'
        ]
    },
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
