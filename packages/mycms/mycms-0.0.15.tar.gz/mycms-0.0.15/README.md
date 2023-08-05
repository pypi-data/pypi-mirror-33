
MyCMS - Yet Another Django Based CMS. 

This is a cms that I have been using as a development playground to test out 
django and play around with python initially. I have used it in production at 
jnvilo.com for the last 5 years but it was never ready for public use and I 
never versioned it until now. I am iteratively preparing it for public consumption. 

Build Requirements

Centos: 

	yum -y install npm gcc
	make

Windows/WSL 

	Since this is a linux environment , we can work like in Linux 
	apt-get install nmp gcc
	make

Windows:

	TODO: Figure out how to install and develop on windows. 
	For now have to use WSL on windows 10. 

Test
----

    make test

Development:

	The makefiles will create a virtualenv and install the module.

Overrides
---------

- `python` version:

        make PYTHON_VERSION='2.7.8' test
        make PYTHON_VERSION='2.7.8' virtualenv
- `pep8` options:

        make PEP8_OPTIONS='--max-line-length=120' python-pep8

If you have already downloaded the tarballs you need (Python and/or virtualenv) you can work offline like this:

    make ONLINE=false virtualenv
