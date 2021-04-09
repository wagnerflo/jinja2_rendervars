from pathlib import Path
from setuptools import setup,Extension

setup(
    name="jinja2_rendervars",
    description="Use Jinja templates to render more than just strings.",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    version="0.1",
    author="Florian Wagner",
    author_email="florian@wagner-flo.net",
    url="https://github.com/wagnerflo/jinja2_rendervars",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: C",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Text Processing",
    ],
    license_files=["LICENSE"],
    python_requires=">=3.7",
    ext_modules=[
        Extension(
            "jinja2_rendervars._contextvars",
            sources=["jinja2_rendervars/_contextvars.c"],
        ),
    ],
    packages=[
        "jinja2_rendervars",
    ],
)
