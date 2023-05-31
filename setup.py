from setuptools import setup, find_packages

setup(
    name='cone-commands',
    packages=find_packages(exclude=['local_tests', 'tests']),
    version='1.0.0',
    install_requires=[
        "py-cone>=1.0.8",
    ],
    include_package_data=True,
    author='cone387',
    maintainer_email='1183008540@qq.com',
    license='MIT',
    url='https://github.com/cone387/cone-commands.git',
    python_requires='>=3.7, <4',
)
