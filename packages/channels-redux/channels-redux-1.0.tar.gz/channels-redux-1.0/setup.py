import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="channels-redux",
    description="Channels-Redux is a package that notifies subscribers about changes in the database",
    version="1.0",
    license='MIT License',
    include_package_data=True,
    author="Johnathan Ryan Hornik",
    author_email="ryanhornik@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/plus1tables/channels-redux-python/",
    packages=setuptools.find_packages(),
    classifiers=(
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ),
    install_requires=[
        "Django>=1.11",
        "djangorestframework>=3.4.0",
        "channels>=2.0.0",
    ]
)
