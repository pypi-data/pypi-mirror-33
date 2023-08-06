from setuptools import setup, find_packages

setup(
    name="skyscraper",
    description="YAML based lightweight crawlers",
    url="https://gitlab.com/woning-group/libs/skyscraper",
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    version="0.0.5",
    packages=find_packages(),
    install_requires=[
        'woning-wattle',
        'click',
        'requests',
        'beautifulsoup4'
    ],
    entry_points={
        'console_scripts': [
            'skyscraper = skyscraper.cli:cli'
        ]
    },
    extras_require={
        'dev': ['woning-bricks']
    }
)
