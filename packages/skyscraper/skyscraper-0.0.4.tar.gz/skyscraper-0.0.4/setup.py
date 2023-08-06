from setuptools import setup, find_packages

setup(
    name="skyscraper",
    description="YAML based lightweight crawlers",
    url="https://gitlab.com/woning-group/libs/skyscraper",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version="0.0.4",
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
