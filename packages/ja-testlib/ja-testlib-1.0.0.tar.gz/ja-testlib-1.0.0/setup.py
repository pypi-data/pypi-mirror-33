

from setuptools import setup

def readme_file():
    with open("README.rst", encoding="utf-8") as rf:
        return rf.read()

setup(name="ja-testlib",
      version="1.0.0",
      description="just a test lib",
      packages=["testlib"],
      py_modules=["tool"],
      author="jacob",
      author_email="312@qq.com",
      long_description=readme_file(),
      url="https://github.com",
      license="MIT")
