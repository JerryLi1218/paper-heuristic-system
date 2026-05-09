from setuptools import find_packages, setup

setup(
    name="paper-heuristic-system",
    version="0.2.0",
    description="A plug-and-play skill and CLI for iterative paper revision, citation verification, and novelty risk mapping.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    python_requires=">=3.9",
    entry_points={"console_scripts": ["paper-hs=paper_hs.cli:main"]},
)
