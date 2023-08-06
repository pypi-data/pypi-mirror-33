.. contents:: Table of Contents:

About
-----

Let's SUN:sunny:(shine)!!!


SUN (Slackware Update Notifier) is a tray notification applet for informing about
package updates in Slackware and CLI tool for monitoring upgraded packages.

.. image:: https://gitlab.com/dslackw/images/raw/master/sun/sun.png
    :target: https://gitlab.com/dslackw/sun

How works
---------

Actually read the two dates of ChangeLog.txt files one the server and a local by counting
how many packages have been upgraded, rebuilt or added.
SUN works with `slackpkg <http://www.slackpkg.org/>`_ as well with `slpkg <https://gitlab.com/dslackw/slpkg>`_
 

Installing
----------

.. code-block:: bash

    Required root privileges

    $ tar xvf sun-1.2.2.tar.gz
    $ cd sun-1.2.2
    $ ./install.sh

    Installed as Slackware package

    or

    $ pip install sun --upgrade


Usage
-----

Choose ONE mirror from '/etc/slackpkg/mirrors' file.


Gtk menu icon
-------------

Add sun in your windows manager session startup.

As for xfce:
Settings Manager --> Session and Startup --> Application Autostart --> +Add

.. code-block:: bash
    
    [Add application]

    Name: sun
    Description: Slackware Update Notifier
    Command: /usr/bin/sun_gtk &
    
    Click [Ok]

    Click Menu --> System --> SUN (Slackware Update Notifier)
    An icon will appear in the panel, right click in SUN icon to show menu.

    Thats it.
    
CLI
---

.. code-block:: bash

    $ sun help
    SUN (Slackware Update Notifier) - Version: 1.2.2

    Usage: sun [OPTION]

    Optional arguments:
      help     display this help and exit
      start    start sun daemon
      stop     stop sun daemon
      restart  restart sun daemon
      check    check for software updates
      status   sun daemon status
      info     os information

    $ sun start
    Starting SUN daemon:  /usr/bin/sun_daemon &

    $ sun stop
    Stopping SUN daemon:  /usr/bin/sun_daemon

    $ sun status
    SUN is not running
    
    $ sun check
    3 software updates are available

    samba-4.1.17-x86_64-1_slack14.1.txz:  Upgraded.
    mozilla-firefox-31.5.0esr-x86_64-1_slack14.1.txz:  Upgraded.
    mozilla-thunderbird-31.5.0-x86_64-1_slack14.1.txz:  Upgraded.


Configuration files
-------------------

.. code-block:: bash

    /etc/sun/sun.conf
        General configuration of sun

    
Screenshots
-----------

.. image:: https://gitlab.com/dslackw/images/raw/master/sun/gtk_daemon.png
    :target: https://gitlab.com/dslackw/sun


.. image:: https://gitlab.com/dslackw/images/raw/master/sun/xfce_screenshot.png
    :target: https://gitlab.com/dslackw/sun


.. image:: https://gitlab.com/dslackw/images/raw/master/sun/kde_screenshot.png
    :target: https://gitlab.com/dslackw/sun


.. image:: https://gitlab.com/dslackw/images/raw/master/sun/check_updates.png
    :target: https://gitlab.com/dslackw/sun

 
Donate
------

If you feel satisfied with this project and want to thanks me make a donation.

.. image:: https://gitlab.com/dslackw/images/raw/master/donate/paypaldonate.png
   :target: https://www.paypal.me/dslackw


Copyright 
---------

- Copyright 2015-2018 © Dimitris Zlatanidis
- Slackware® is a Registered Trademark of Patrick Volkerding.
- Linux is a Registered Trademark of Linus Torvalds.
