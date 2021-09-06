import setuptools

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

setuptools.setup(
    name="dico-command",
    version="0.0.1",
    author="eunwoo1104",
    author_email="sions04@naver.com",
    description="Command handler for dico.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dico-api/dico-command",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=["dico-api"],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
