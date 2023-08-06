from setuptools import setup

setup(
    name='elsewhere-db',
    version='0.1',
    description='Model for ordering menu and users',
    url='https://gitlab.com/piar301/auth0-login',
    author='Billy Lapatas',
    author_email='piar301@gmail.com',
    license='MIT',
    packages=['ew_db'],
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'PyMySQL',
    ],
    zip_safe=False,
)
