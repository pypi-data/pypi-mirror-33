from setuptools import setup
import os

setup(
    name='my-awesome-package',
    version='0.1.%s' % os.environ.get('TRAVIS_BUILD_NUMBER', 0),
    description='My awesome package',
    author='Me',
    author_email='info@python-private-package-index.com',
    license='MIT',
    packages=['my-awesome-package'],
    url='https://gitlab.com/pypri/pypri-gitlab-ci',
    zip_safe=False
)