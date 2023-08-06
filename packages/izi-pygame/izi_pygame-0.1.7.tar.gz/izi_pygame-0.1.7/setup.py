import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="izi_pygame",
    version="0.1.7",
    author="Dave Tilheim",
    author_email="mb624967@skynet.be",
    description="A small package who's made pygame easier about the drawing rects, the pictures, the fonts and the windows. You have to install pygame. To import write: import izi_pygame"
    + " In the 0.1.7 version -> Picblock bug is fixed. Call izi_pygame.doc() the github of the project will open. dowload project and open /doc/index.html with your browser."
    + " A DOCUMENTATION is also available on my github (the same as izi_pygame.doc()), read it if you want to understand the role of this package!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DaveTilheim/izi-pygame",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ),
)