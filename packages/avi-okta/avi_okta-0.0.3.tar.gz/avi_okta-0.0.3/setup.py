import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="avi_okta",
    version="0.0.3",
    author="Neel Parikh",
    author_email="nparikh@avinetworks.com",
    description="Avi Networks Okta sdk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avinetworks/avi-internal",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
	"Programming Language :: Python :: 2",
    	"Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

