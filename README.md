## Simple machine ssh manager

Use a definitions file `machine-set.csv` and a set of known public keys
located in `public-keys` to manage user-access to a series of machines over ssh by changing the `authorized_keys` files remotely (over ssh).
Requires certificate access to the machines in the first instance.

### run
First update the `machine-set.csv` to match your server setup, then run `python3 update-ssh.py`

### machine-set.csv format

An example is shown below 

| machine ip or hostname | ssh port | ssh user | ssh private key path   | ssh public key path        | user names        |
|------------------------|----------|----------|------------------------|----------------------------|-------------------|
| some-server            | 22       | ssh-user | connection-keys/id_rsa | connection-keys/id_rsa.pub | rock, rock_laptop |

where:

| field                  | description                                                                                                                                          |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| machine ip or hostname | is the ip address or FQDN of the server you wish to check / change access to                                                                         |
| ssh port               | the ssh port (default 22) to use for comms with the server                                                                                           |
| ssh private key path   | a path to the private key to be used for communications with the server                                                                              |
| ssh public key path    | a path to the public key associated with the above private key to ensure continuned communications                                                   |
| ssh keys / user names  | a CSV list of users whose public keys must be in the `public-keys/` folder of this program the format for the public key is `<user-name>_id_rsa.pub` |

Copy all required public keys (format `<user-name>_id_rsa.pub`) into the `public-keys/` folder.
The above example thus assumes there is a machine called `some-server` that is accessible over ssh using a user-account called `ssh-user`.
For this to work you should be able to run `ssh -i connection-keys/id_rsa ssh-user@some-server` and connect.  Port 22 in this case is the default ssh port.

These public keys referenced by the `user names` must exist and are checked on startup.  The public keys themselves must be the copy of the original
ssh public key-file from your users.  Do not add anything to these files!  They must be single-line entries as they originally would have been.

This program then reads the `authorized_keys` file located at `/home/<ssh_user>/.ssh/authorized_keys`, where `<ssh_user>` is the name referenced by
the `machine-set.csv`.  It parses this file and sees what public keys it recognizes and what keys need to be removed / added.

If there are any changes, this program will create a new temporary `authorized_keys` file and copy it to the remote machine.
This program backs up the original `/home/<ssh-user>/.ssh/authorized_keys` to `/home/<ssh-user>/.ssh/authorized_keys.backup`.
It then overwrites the existing file of the same name located at `/home/<ssh-user>/.ssh/authorized_keys`.

This program will also copy the `connection-keys/id_rsa.pub` into the `authorized_keys` ensuring continued access to each server by this utility even if you forget.
