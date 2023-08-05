from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


def version():
    with open('hanna/VERSION') as f:
        return f.read()

setup(
    name='hanna',
    version=version(),
    description='Turns your configurations into actions',
    long_description=readme(),
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ],
    keywords=['configuration', 'framework'],
    url='https://gitlab.com/Dominik1123/Hanna',
    author='Dominik Vilsmeier',
    author_email='dominik.vilsmeier1123@gmail.com',
    license='BSD-3-Clause',
    packages=[
        'hanna',
        'hanna.physics',
    ],
    install_requires=[
        'pyhocon',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False
)
