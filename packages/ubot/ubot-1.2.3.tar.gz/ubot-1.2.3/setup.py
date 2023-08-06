from setuptools import find_packages, setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='ubot',
    version='1.2.3',
    author='Alessandro Cerruti',
    author_email='thereap3r97@gmail.com',
    description='Basic, easily extendable, Telegram bot class',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/strychnide/ubot',
    license='MIT',
    project_urls={
        'Source': 'https://github.com/strychnide/ubot',
        'Issues': 'https://github.com/strychnide/ubot/issues'
    },
    python_requires='>=3.5',
    install_requires=[
        'urllib3',
        'certifi'
    ],
    extras_require={
        'dev': [
            'flake8',
            'flake8-sorted-keys',
            'flake8-import-order',
            'flake8-quotes',
            'flake8-bugbear',
            'mypy',
            'sphinx',
            'sphinx-autodoc-typehints',
            'sphinx_rtd_theme',
            'coverage'
        ]
    },
    packages=find_packages()
)