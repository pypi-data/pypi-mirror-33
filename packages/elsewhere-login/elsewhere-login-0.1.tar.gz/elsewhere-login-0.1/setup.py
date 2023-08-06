from setuptools import setup

setup(
    name='elsewhere-login',
    version='0.1',
    description='Authentication wrapper for Auth0',
    url='https://gitlab.com/piar301/auth0-login',
    author='Billy Lapatas',
    author_email='piar301@gmail.com',
    license='MIT',
    packages=['ew_login'],
    install_requires=[
        'Flask',
        'flask-oidc',
    ],
    zip_safe=False,
)
