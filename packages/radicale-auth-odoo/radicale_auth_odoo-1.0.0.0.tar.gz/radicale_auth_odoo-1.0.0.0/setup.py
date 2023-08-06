from setuptools import setup

def requires():
    try:
        with open('requirements.txt', 'r') as rfile:
            lines = rfile.read().splitlines()
    except FileNotFoundError:
        lines = []
    return lines

setup(
    name="radicale_auth_odoo",
    version="1.0.0.0",
    description="Odoo Authenticaiton Plugin for Radicale 2",
    author="Hugo Rodrigues",
    author_email="me@hugorodrigues.net",
    license="BSD-3-Clause",
    url="https://git.hugorodrigues.net/hugorodrigues/radicale_auth_odoo",
    packages=["radicale_auth_odoo"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        ],
    install_requires=requires()
    )
