from setuptools import setup

setup(
    name="masonite-entry",
    version='2.0.0',
    packages=[
        'entry',
        'entry.api',
        'entry.api.models',
        'entry.api.auth',
        'entry.api.controllers',
        'entry.api.middleware',
        'entry.commands',
        'entry.migrations',
        'entry.providers',
    ],
    install_requires=[
        'PyJWT==1.6.4'
    ],
    include_package_data=True,
)
