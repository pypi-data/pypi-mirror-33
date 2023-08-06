from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='grandmasomsri',
    version='0.3',
    description='Grandma Somsri and Grandpa Prayud',
    long_description=readme(),
    url='https://github.com/SOMSRICAT/grandmasomsri',
    author='SomsriCat',
    author_email='s.wuttiprasit@gmail.com',
    license='Somsri',
    install_requires=[
        'matplotlib',
        'numpy',
    ],
    scripts=['bin/grandmasomsri-status',
             'bin/grandpaprayud-status',
             'bin/graph-power'],
    keywords='grandmasomsri grandpaprayud somsri prayud',
    packages=['grandmasomsri'],
    package_dir={'grandmasomsri': 'src/grandmasomsri'},
    package_data={'grandmasomsri': ['graph/*.py']
    },
)