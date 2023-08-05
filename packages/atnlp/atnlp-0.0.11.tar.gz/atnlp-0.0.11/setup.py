from setuptools import find_packages, setup
from glob import iglob
import os

# paths
TOPDIR = os.path.dirname(__file__)
ATNLP = os.path.join(TOPDIR,'atnlp')
SCRIPTS = os.path.join(TOPDIR, 'scripts')
SHARE = os.path.join(ATNLP, 'share')

# scripts
script_exts = ['*.py', '*.sh']
scripts = [p for ext in script_exts for p in
           iglob(os.path.join(SCRIPTS,'**',ext), recursive=True)]
# data
data_exts = ['*.py', '*.yml']
data = [os.path.relpath(f, ATNLP) for ext in data_exts
        for f in iglob(os.path.join(SHARE,'**',ext),recursive=True)]

# requirements
install_requires=[
    "matplotlib",
    "nltk",
    "numpy",
    "pandas",
    "pyyaml",
    "scikit-learn",
    "scipy",
    "seaborn",
    "xgboost",
]
extras_requires={
    'deep': ['gensim', 'keras', 'tensorflow'],
    'book': ['ipykernel', 'ipython', 'jupyter', 'notebook'],
    'docs': ['sphinx', 'sphinx_rtd_theme'],
    'dev': ['bumpversion']
}
extras_requires['extras'] = list(set([a for b in extras_requires.values() for a in b]))

setup(
    name='atnlp',
    description='A tool for natural language processing in python based on scipy and sklearn',
    long_description=open(os.path.join(TOPDIR, 'README.md')).read(),
    long_description_content_type='text/markdown',
    url='https://github.com/wedavey/atnlp',
    author='Will Davey',
    author_email='wedavey@gmail.com',
    license='MIT',
    packages=find_packages(),
    package_data={'atnlp':data},
    python_requires=">=3.5",
    install_requires=install_requires,
    extras_require=extras_requires,
    scripts=scripts,
    version='0.0.11',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
