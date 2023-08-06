import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="avi_okta",
    version="0.0.9",
    author="Neel Parikh",
    author_email="nparikh@avinetworks.com",
    description="Avi Networks Okta sdk",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/avinetworks/avi-internal",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'backoff',
        'jinja2',
        'sendgrid',
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

