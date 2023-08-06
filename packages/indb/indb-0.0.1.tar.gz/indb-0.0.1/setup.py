from setuptools import find_packages, setup

setup(
    name='indb',
    version='0.0.1',
    description='Infinity database.',
    url='https://gitlab.com/infamily/indb',
    author='Mindey',
    author_email='mindey@qq.com',
    license='AGPL',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=[],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
