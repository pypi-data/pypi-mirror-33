============
Installation
============


Windows
=======

#. Install *Python 2.7.9*

    * Download `Python 2.7.9 Windows X86-64 Installer`_
    * Double click to run the installer.


#. Install *Python for Windows extensions*

    * Download `pywin32-220.win-amd64-py2.7.exe`_
    * Double click to run the installer.


#. Install *Setuptools*

    * Download `ez_setup.py`_
    * Go to folder
    * Shift-right-click
    * Click *Open command window here*
    * Run::

        C:\Python27\python.exe ez_setup.py


#. Install *pcrunner*

    * Download `master.zip`_::

        curl -o master.zip https://codeload.github.com/maartenq/pcrunner/zip/master

    * Go to folder
    * Shift-right-click
    * Click *Open command window here*
    * Run::

        C:\Python27\Scripts\easy_install.exe master.zip


#. Install *pcrunner* as Windows Service

    * Go to folder ``C:\Python27\Lib\site-packages\pcrunner-0.3.9-py2.7.egg\pcrunner``
    * Shift-right-click
    * Click *Open command window here*
    * Run::

        C:\Python27\python.exe windows_service.py install


#. Configure *pcrunner* as Windows Service

    * Edit ``C:\Python27\Lib\site-packages\pcrunner-0.3.9-py2.7.egg\pcrunner\etc\pcrunner.yml``
        * *nsca_web_url*
        * *nsca_web_username*
        * *nsca_web_password*


#. Start *pcrunner* as Windows Service

    * *Start* -> *Administrative Tools* -> *Services*
    * Select *pcrunner*
    * Click start


Linux with virtualenv
=====================

Installation on Fedora/RH/Centos/SL

.. note::

    * Commands with a '#' prompt must be run as root.
    * Commands with a '$' prompt must be run as a non-root user.
    * 'sudo' is used when a reverence to a home directory (~) is used in the
      command line.


#. Download *pcrunner*::

    # curl -O https://github.com/maartenq/pcrunner/archive/master.zip


#. Install python-virtualenv_::

    # yum install python-virtualenv


#. Make virtual environment::

    # virtualenv /<path>/<to>/<virtualenv_dir>


#. Make virtual environment active::

    # source /<path>/<to>/<virtualenv_dir>/bin/activate


#. Install *pcrunner*::

    (virtenv)# pip install master.zip


#. Install configuration files::

    # mkdir /etc/pcrunner
    # mkdir /var/spool/pcrunner
    # install -m 640 /<path>/<to>/<virtualenv_dir>/lib/python2.6/site-packages/pcrunner/etc/pcrunner.yml /etc/pcrunner/pcrunner.yml
    # install -m 644 /<path>/<to>/<virtualenv_dir>/lib/python2.6/site-packages/pcrunner/etc/commands.yml /etc/pcrunner/commands.yml
    # install -m 755 /<path>/<to>/<virtualenv_dir>/lib/python2.6/site-packages/pcrunner/etc/pcrunner_rh_init /etc/init.d/


#. Edit configuration files::

    # vim /etc/pcrunner/pcrunner.yml
    # vim /etc/pcrunner/commands.yml


#. Check the config::

    # chkconfig pcrunner on


#. Start the service::

    # service pcrunner start


Linux RPM
=========

#. Install packages for RPM Build Environment::

    $ sudo yum install rpm-build
    $ sudo yum install python-devel
    $ sudo yum install python-setuptools


#. Create directories for RPM Build Environment::

    $ mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}


#. Create RPM macro file::

    $ echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros


#. Download pcrunner-0.3.9.tar.gz from `GitHub`::

    $ curl -L -o pcrunner-0.3.9.tar.gz https://github.com/maartenq/pcrunner/archive/v0.3.9.tar.gz


#. Build RPM from tarball::

    $ rpmbuild -tb pcrunner-0.3.9.tar.gz


#. Install RPM::

   $ sudo yum install ~/rpmbuild/RPMS/noarch/pcrunner-0.3.9-1.noarch.rpm


#. Edit configuration files::

    $ sudo vim /etc/pcrunner/pcrunner.yml
    $ sudo vim /etc/pcrunner/commands.yml


#. Check the config::

    $ sudo chkconfig pcrunner on


#. Start the service::

    $ sudo service pcrunner start


.. _Python 2.7.9 Windows X86-64 Installer: https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi

.. _pywin32-220.win-amd64-py2.7.exe: http://downloads.sourceforge.net/project/pywin32/pywin32/Build%20220/pywin32-220.win-amd64-py2.7.exe?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fpywin32%2Ffiles%2Fpywin32%2FBuild%2520220%2F&ts=1471597280&use_mirror=freefr

.. _ez_setup.py: https://bootstrap.pypa.io/ez_setup.py

.. _master.zip: https://codeload.github.com/maartenq/pcrunner/zip/master

.. _python-virtualenv: https://virtualenv.pypa.io/
