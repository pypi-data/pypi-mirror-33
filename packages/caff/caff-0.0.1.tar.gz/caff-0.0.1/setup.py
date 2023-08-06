from setuptools import setup
import os

setup(
    name="caff",
    version="0.0.1",
    py_modules=["caff"],
    url="https://github.com/skar404/coffee",
    author="User Name",
    author_email="skar404@gmail.com",
    description="Text to coffee morse code and coffee morse to text",
    long_description=open("README.md").read() if os.path.isfile("README.md") else "",
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["coffee=caff:caff"]},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)