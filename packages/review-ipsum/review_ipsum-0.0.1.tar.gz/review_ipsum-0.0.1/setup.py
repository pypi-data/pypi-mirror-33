import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="review_ipsum",
    version="0.0.1",
    author="Jake Barber",
    author_email="jake.b.dev@gmail.com",
    description="Review Themed Lorem Ipsum",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JakeBar/review-ipsum",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
