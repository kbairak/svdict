from setuptools import find_packages, setup

setup(name="svdict",
      version="0.1",
      packages=find_packages(),
      install_requires=['jsonschema'],
      package_dir={'': 'src'},
      author="Konstantinos Bairaktaris",
      author_email="kbairak@transifex.com",
      description="Self-validating dicts/lists using jsonschema",
      keywords="data-types validation jsonschema domain-models",
      url="https://github.com/kbairak/svdict",
      project_urls={'Source Code': "https://github.com/kbairak/svdict"})
