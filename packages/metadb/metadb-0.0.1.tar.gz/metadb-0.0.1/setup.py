from setuptools import find_packages, setup

setup(
    name='metadb',
    version='0.0.1',
    description='A pattern of types theory to mongodb.',
    url='https://gitlab.com/wefindx/metadb',
    author='Mindey',
    author_email='mindey@qq.com',
    license='ASK FOR PERMISSIONS',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=["pymongo", "typology", "metaform", "requests", "progress"],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
