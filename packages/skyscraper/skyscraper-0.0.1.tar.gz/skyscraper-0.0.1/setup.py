from setuptools import setup, find_packages

setup(
    name="skyscraper",
    description="YAML based lightweight crawlers",
    version="0.0.1",
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
