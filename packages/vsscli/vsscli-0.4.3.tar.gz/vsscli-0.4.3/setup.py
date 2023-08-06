from setuptools import setup, find_packages
import os
import vsscli
import io


def read(fname):
    with io.open(os.path.join(os.path.dirname(__file__), fname),
                 encoding='utf-8') as fo:
        return fo.read()


with io.open('requirements.txt', encoding='utf-8') as f:
    required = f.read().splitlines()

setup(name='vsscli',
      version=vsscli.__version__,
      description='ITS Private Cloud Command Line Interface',
      author='University of Toronto - ITS',
      author_email='jm.lopez@utoronto.ca',
      maintainer='Virtualization & Storage Services',
      maintainer_email='vss-py@eis.utoronto.ca',
      url='https://eis.utoronto.ca/~vss/vsscli/',
      download_url='https://gitlab-ee.eis.utoronto.ca/vss/vsscli/tags',
      install_requires=required,
      packages=find_packages(exclude=['tests*']),
      include_package_data=True,
      scripts=['bin/vss_bash_completer'],
      package_data={'vsscli': ['bin/*']},
      entry_points='''
        [console_scripts]
        vss=vsscli.cli:cli
        ''',
      license='MIT License',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6'
      ],
      platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix', 'OpenBSD'],
      zip_safe=False
      )
