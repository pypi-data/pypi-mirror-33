from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='minimal_validator',
      version='0.1.3',
      description='Minimal validation framework',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development',
      ],
      keywords='validation',
      url='https://github.com/nestedsoftware/minimal_validator',
      author='Nested Software',
      author_email='2969361+nestedsoftware@users.noreply.github.com',
      license='MIT',
      packages=['minimal_validator'],
      install_requires=[
          'email_validator',
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      include_package_data=True,
      zip_safe=False)
      
