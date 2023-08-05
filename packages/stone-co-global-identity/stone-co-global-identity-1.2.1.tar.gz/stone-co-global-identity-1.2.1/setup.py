from setuptools import find_packages, setup

setup(name="stone-co-global-identity",
      version="1.2.1",
      description="Global Identity Authentication PIP",
      long_description=open("README.md").read().strip(),
      long_description_content_type="text/markdown",
      author="Customer Satisfaction",
      author_email="jfreitas@stone.com.br",
      url="https://github.com/stone-payments/globalidentity-python",
      packages=find_packages(exclude=["examples", "tests"]),
      py_modules=["global_identity"],
      install_requires=["requests",
                        "pytest",
                        "setuptools",
                        "urllib3",
                        "certifi",
                        "idna"],
      license="MIT License",
      zip_safe=True,
      keywords="global identity",
      classifiers=[
            "Topic :: System :: Systems Administration :: Authentication/Directory"
            ]
      )
