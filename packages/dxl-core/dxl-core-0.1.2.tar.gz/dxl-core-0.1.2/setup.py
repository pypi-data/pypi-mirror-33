from setuptools import setup, find_packages
setup(
    name='dxl-core',
    version='0.1.2',
    description='Core utility library.',
    url='https://github.com/Hong-Xiang/dxcore',
    author='Hong Xiang',
    author_email='hx.hongxiang@gmail.com',
    license='MIT',
    namespace_packages=['dxl'],
    packages=find_packages('src/python'),
    package_dir={'': 'src/python'},
    install_requires=[],
    zip_safe=False)
