# properly-util-python


## Quick Run

1. Setup the environment for development by calling ./setup.sh
2. Make your changes to the code
3. Increase the `major` or `minor` values in if appropriate [setup.py](https://github.com/GoProperly/properly-util-python/blob/master/setup.py#L8)
4. Run `./tests.sh` to run automated tests.



## Uploading the Package

To upload package.

You can either: 
Merge changes to master branch and push.

*NOTE: You do not need to upload the package, it is uploaded automatically on a merge of a branch to master.* 

OR manually uplaod package to pypi
5. `source deploy.sh`
6.  `deploy.sh "<your_commit_message>" <version>`

Make sure you have the latest versions of setuptools and wheel installed:

`python3 -m pip install --user --upgrade setuptools wheel`

You’ll need to install Twine:

`python3 -m pip install --user --upgrade twine`

Build dist/

`python3 setup.py sdist bdist_wheel`

Upload to pypi.org
`twine upload dist/*`

Source: https://packaging.python.org/tutorials/packaging-projects/


## Installing the Package 

`pip install properly-util-python`

or

`pip install --no-cache-dir --upgrade properly-util-python`


Archived info, installing directly from github: 
`pip install -e git+https://github.com/GoProperly/properly-util-python.git#egg=properly-util-python`

Note: -e indicates that extra-url-info is saved for pip freeze: https://pip.pypa.io/en/stable/reference/pip_wheel/#extra-index-url


## Resources

see:https://stackoverflow.com/questions/15268953/how-to-install-python-package-from-github#comment37317873_15268990

Based on this tutorial:
http://greenash.net.au/thoughts/2015/06/splitting-a-python-codebase-into-dependencies-for-fun-and-profit/

Private repos possible through vendors like JFrog and their artifactory product
