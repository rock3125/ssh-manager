## Simple machine ssh manager

Use a definitions file `machine-set.csv` and a set of known public keys
located in `public-keys` to manage access to a series of machines.

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

The *hardest* part is gathering the existing public keys.  Copy each key from any/all machines you need and prepend each key with a name.
The above example thus assumes there is a machine called `some-server` that is accessible over ssh using a user-account called `ssh-user`.
For this to work you should be able to run `ssh -i connection-keys/id_rsa ssh-user@some-server` and connect.  
Port 22 in this case is the default ssh port and doesn't change anything.

The program in this case also assumes that there are two ssh keys in the `public-keys/` folder named `rock-id_rsa.pub` and `rock_laptop-id_rsa.pub`.
Make sure you don't add any extra hyphens (-) to the name as it takes the name part from the filename.  So `rock_laptop-id_rsa.pub` in the
code becomes `username = "rock_laptop-id_rsa.pub".split('-')[0]`.

These public keys referenced by the users must exist and are checked on startup.  The public keys themselves must be the copy of the original
ssh key-file from your machines.  Do not add anything to these files!  They must be single-line entries as they originally would have been.

This program reads the `authorized_keys` file located at `/home/<ssh_user>/.ssh/authorized_keys`, where `<ssh_user>` is the name referenced by
the `machine-set.csv` file as `ssh-user` as shown above.

This program compares the differences, does not act if there are no changes to be made.  If there are any changes, this program will
create a new temporary `authorized_keys` file and copy it to the remote machine, overwriting the existing file of the same name located
at `/home/<ssh-user>/.ssh/authorized_keys`.

This program backs up the original `/home/<ssh-user>/.ssh/authorized_keys` to `/home/<ssh-user>/.ssh/authorized_keys.backup`.
This program will also copy the `connection-keys/id_rsa.pub` into the `authorized_keys` ensuring continued access to each server by this utility even if you forget.

### run
First update the `machine-set.csv` to match your server setup, then run `python3 update-ssh.py`
