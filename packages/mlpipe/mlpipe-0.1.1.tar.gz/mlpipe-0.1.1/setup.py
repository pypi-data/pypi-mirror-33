import setuptools

setuptools.setup(
    name='mlpipe',
    version='0.1.1',
    author='Longbin Chen',
    author_email='lbchen@gmail.com',
    packages=['mlpipe',],
    scripts=['mlpipe/django/manage.py',],
    license='LICENSE.txt',
    url='https://github.com/LongbinChen/mlpipe',
    description='A toolkit to manage machine learning libraries.',
    long_description=open('README.md').read(),
    install_requires=[
        "Django >= 1.8.1",
    ],
)
