from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = [
    "langai_client"
]

install_requires = [
    "requests>=2.18"
]

setup(
    name="langai-client",
    version="0.0.1",
    author="Lang.ai",
    author_email="info@lang.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="A LangAI API client written in Python.",
    url="https://github.com/lang-ai/langai-python",
    license="MIT",
    packages=packages,
    keywords="lang.ai api client",
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)