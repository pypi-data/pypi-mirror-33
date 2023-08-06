
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pylocalytics',
    url='https://github.com/zhilevan/pylocalytics',
    author='Zhilevan Ibra',
    author_email='zhilevan@gmail.com',
    packages = ['pylocalytics'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='1.0',
    license='MIT',
    description='Python API Client for Localytics Raw Data Export and Audience Export'
)
