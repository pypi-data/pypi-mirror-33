import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, "doodledashboarddisplay", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about['__name__'],
    version=about['__version__'],
    description="Library for building new displays for Doodle-Dashboard.",
    url="https://github.com/SketchingDev/Doodle-Dashboard-Display",
    license="MIT",
    packages=["doodledashboarddisplay"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.4"
    ],
    python_requires=">=3.4"
)
