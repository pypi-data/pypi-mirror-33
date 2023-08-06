from setuptools import setup, find_packages
setup(
    name='dxl-function',
    version='0.0.1',
    description='Functional library.',
    url='https://github.com/Hong-Xiang/dxfunction',
    author='Hong Xiang',
    author_email='hx.hongxiang@gmail.com',
    license='Apache 2.0',
    namespace_packages=['dxl'],
    packages=find_packages('src/python'),
    package_dir={'': 'src/python'},
    install_requires=[],
    zip_safe=False)

