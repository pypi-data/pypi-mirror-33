from distutils.core import setup
from setuptools import find_packages

requirements = [
    'Django>=1.11.3,<2',

    # Used for partial indexes in Matchup model
    'django-partial-index>=0.4.0,<0.5',

    # Required for ImageField in Matchup model
    'Pillow>=5.1.0,<6',

    # Require Postgres -- can't use sqlite because some models use
    # django.contrib.postgres.fields.ArrayField
    'psycopg2>=2.7.1,<3',

    # Library for querying box office data
    'pybomojo>=0.1.1,<0.2',

    # Create slugs from matchup titles
    'python-slugify>=1.2.4,<2',
]

test_requirements = [
    # Used in test settings
    'dj-database-url==0.4.2',

    # Libraries used by the tests themselves
    'freezegun==0.3.10',
    'mock==2.0.0',

    # Libraries used to discover/run the tests
    'pytest==3.2.0',
    'pytest-django==3.1.2',
]

setup(
    name='bomojo',
    packages=find_packages(),
    version='0.7.9',
    description='Django app for getting movie box office data',
    python_requires='>=3.6',
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require={
        'test': test_requirements
    },
    author='Dan Tao',
    author_email='daniel.tao@gmail.com',
    url='https://bitbucket.org/dtao/pybomojo',
    keywords=[],
    classifiers=[],
)
