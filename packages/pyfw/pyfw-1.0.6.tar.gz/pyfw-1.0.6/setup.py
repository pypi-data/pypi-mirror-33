from setuptools import setup, find_packages
import re, os



requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()



version = ''
with open('__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.md') as f:
    readme = f.read()



setup(
        name = "pyfw",
        version = version,
        keywords = ("pip", "pathtool","timetool", "magetool", "mage"),
        description = "python framework",
        long_description = readme,
        license = "MIT Licence",

        url = "https://github.com/wenanguo/crm",
        author = "Andrew Wen",
        author_email = "wenanguo110@163.com",

        packages = find_packages(),
        include_package_data = True,
        platforms = "any",
        install_requires = requirements


      # name='pyfw',
      # author='Rapptz',
      # url='https://github.com/Rapptz/discord.py',
      # version=version,
      # packages=['discord', 'discord.ext.commands'],
      # license='MIT',
      # description='A python wrapper for the Discord API',
      # long_description=readme,
      # include_package_data=True,
      # install_requires=requirements
)

