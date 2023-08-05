from setuptools import find_packages, setup

long_description = open("README.md").read()

print(find_packages())

setup(
    name="boardify",
    version="0.5.2",
    description="A web-based dashboard to analyzing your data with Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Lucas Hild",
    author_email="contact@lucas-hild.de",
    url="https://github.com/Lanseuo/boardify",
    packages=["boardify", "boardify.blocks"],
    install_requires=[
        "flask"
    ],
)
