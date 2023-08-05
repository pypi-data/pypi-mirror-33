from setuptools import setup, find_packages

setup(
    name="wagtail-links",
    version="2.0.0",
    author="David Burke",
    author_email="david@thelabnyc.com",
    description="Wagtail links provides a consistent way to refer to links in a wagtail page",
    license="Apache License",
    keywords="django wagtail",
    url="https://gitlab.com/thelabnyc/wagtail-links",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Wagtail',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: Apache Software License",
    ],
    install_requires=[
        'wagtail>=2.0',
    ],
    extras_require={
        'development': [
            'flake8>=3.3.0',
            'tox>=2.7.0',
        ],
    },
)

