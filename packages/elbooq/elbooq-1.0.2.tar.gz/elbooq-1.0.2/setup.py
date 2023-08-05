from setuptools import setup
with open("README.md", "r") as fh:
    long_description = fh.read()
requires = ['requests',]
setup(name='elbooq',
      version='1.0.2',
      description='Client to Elbooq Payment Gateway',
      url='https://www.bitbucket.org/labelag/elbooq',
      author='Elbooq',
      author_email='wecare@elbooq.net',
      license='MIT',
      packages=['elbooq'],
      install_requires=requires,
      classifiers=[
	"Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      zip_safe=False)
