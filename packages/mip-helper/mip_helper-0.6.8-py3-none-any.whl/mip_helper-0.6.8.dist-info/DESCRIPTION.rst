MIP\_Helper
===========

This is a Python library used in the hbpmip/python-mip Docker image in
order to ease developers job. It provides functions to read and write
data from/to the MIP.

For more details, please have a look at
`python-mip <https://github.com/LREN-CHUV/python-base-docker-images/blob/master/python-mip/README.md>`__.

How to update it
----------------

1) Update the library code, update the version number in the
   **setup.cfg** file and optionally the **.md** version of the README
2) Run the **build.sh** script in order to generate the **.rst** version
   of the README and build the library
3) Commit and push your changes and run the **publish.sh** script in
   order to publish the new release on PyPI


