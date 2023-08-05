from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name="mock_aerohive",
      version="0.0.2",
      description="A mock SSH server emulating Aerohive devices",
      long_description=readme(),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Testing :: Mocking",
      ],
      keywords="aerohive ssh mock server",
      url="https://github.com/pencot/mock_aerohive",
      author="Ryan Leonard",
      license="MIT",
      packages=[
        "mock_aerohive",
      ],
      install_requires=[
        "mockssh >=1.4.5,<2"
      ],
      include_package_data=True)
