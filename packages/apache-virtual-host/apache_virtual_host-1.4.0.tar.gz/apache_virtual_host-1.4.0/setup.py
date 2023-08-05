import os
import setuptools

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name = "apache_virtual_host",
    version = "1.4.0",
    author = "Hizbul Bahar",
    author_email = "hizbul25@gmail.com",
    description = ("Creating virtual host is a time consuming task for starting new project along with complexity. "
                                   "This tools make this process easy. Within a minute you can create your virtual host without any hassle."),
    license = "MIT",
    keywords = "Apache Virtualhost Virtual Host",
    url="https://github.com/hizbul25/apacheVirtualHost",
    long_description=read('README.md'),
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
    packages=setuptools.find_packages(),
)