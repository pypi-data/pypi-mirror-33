from setuptools import setup, find_packages

with open('README.md') as fp:
    long_description = fp.read()

setup(
    name='django-tls-middleware',
    version='0.1.0',
    url='https://github.com/sekomy/django-tls-middleware',
    author='Sekom Yazilim',
    author_email='info@sekomyazilim.com.tr',
    license='MIT',
    description='TLS Middleware',
    long_description=long_description,
    packages=find_packages(exclude=['docs', 'tests*']),
    platforms=['any'],
    include_package_data=True,
)
