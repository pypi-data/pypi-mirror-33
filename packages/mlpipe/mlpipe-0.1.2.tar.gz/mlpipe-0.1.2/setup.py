from setuptools import setup, find_packages
print find_packages(exclude=['mlpipe.django.mlpipe.migrations', 'mlpipe.django.mlpipe.templatetags'])


setup(
    name='mlpipe',
    version='0.1.2',
    author='Longbin Chen',
    author_email='lbchen@gmail.com',
    packages=find_packages(exclude=['mlpipe.django.mlpipe.migrations', 'mlpipe.django.mlpipe.templatetags']),
    package_data={'':['*.yaml',]},
    scripts=['mlpipe/django/manage.py',],
    license='LICENSE.txt',
    url='https://github.com/LongbinChen/mlpipe',
    description='A toolkit to manage machine learning libraries.',
    long_description=open('README.md').read(),
    include_package_data=True,
    install_requires=[
        "Django >= 1.8.1",
    ],
)
