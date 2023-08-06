============
Installation
============

Install DarkSkySync by running::

    $ pip install DarkSkySync
    
Verify if the installation was successful::

	$ DarkSkySync list
    
**Note:** Make sure the darksky host can be accessed over ssh without password prompt. If this is not the case follow the instruction below:

     
How to Set Up a Password-less SSH Login
---------------------------------------

First, on the local machine you will want to generate a secure SSH key::

	$ ssh-keygen -t dsa -P "" -f ~/.ssh/id_dsa_darksky

Next, you need to copy the generated key to the darksky remote server you want to setup passwordless logins with. 

If you have mounted the SAN group drive (astrogate) this is easily done with the following command string but you can use scp if you'd prefer::

	$ cat ~/.ssh/id_dsa_darksky.pub | cat >> /Volumes/astro/refreg/data/.ssh/authorized_keys

Alternatively::

	$ cat ~/.ssh/id_dsa_darksky.pub | ssh <user>@plumpy.ethz.ch 'cat >> /data/astro/refreg/data/.ssh/authorized_keys'

This command takes the generated SSH key from the local machine and then uses cat to append the key file to the remote users authorized key list.

Finally, confirm that you can now login to the remote SSH server without a password::

	$ DarkSkySync avail

