import setuptools

with open("README.md", "rb") as f:
    long_description = f.read().decode("utf-8")
    
setuptools.setup(
    name="psyshort",
    version="0.1.4",
    author="Quit3Simpl3",
    description="Making psycopg2 a little simpler to use.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/Quit3Simpl3/psyshort",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        )
    )

