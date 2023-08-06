import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="whole_history_rating",
    version="1.3.3",
    author="Pierre-François Monville",
    author_email="p_fmonville@hotmail.fr",
    description="A python implementation of the whole-history-rating algorythm by Rémi Coulom",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pfmonville/whole_history_rating",
    # packages=setuptools.find_packages(),
    packages=['whr'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)