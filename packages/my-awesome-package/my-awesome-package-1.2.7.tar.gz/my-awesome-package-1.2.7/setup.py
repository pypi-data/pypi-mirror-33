from setuptools import setup
import os

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = os.environ['CI_JOB_ID']


setup(
    name='my-awesome-package',
    version=version,
    description='My awesome package',
    author='Me',
    author_email='info@python-private-package-index.com',
    license='MIT',
    packages=['my-awesome-package'],
    url='https://gitlab.com/pypri/pypri-gitlab-ci',
    zip_safe=False
)