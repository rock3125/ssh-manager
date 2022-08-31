## Simple machine ssh manager

Use a definitions file `machine-set.csv` and a set of known public keys
located in `public-keys` to manage access to a series of machines.

### machine-set.csv format

An example is shown below 

| machine ip or hostname | ssh port | ssh user | ssh private key path | ssh public key path  | ssh keys / user names |
|------------------------|----------|----------|----------------------|----------------------|-----------------------|
| some-server            | 22       | ssh-user | path/to/id_rsa       | path/to/id_rsa.pub   | rock, rock_laptop     |

The *hardest* part is gathering the existing public keys.  Copy each key from any/all machines you need and prepend each key with a name.
The above example thus assumes there is a machine called `test01-app01` that is accessible over ssh using a user-account called `ssh-user`.
For this to work you should be able to run `ssh -i path/to/id_rsa ssh-user@some-server` and connect.  
Port 22 in this case is the default ssh port and doesn't change anything.

The program in this case also assumes that there are two ssh keys in the `public-keys/` folder named `rock-id_rsa.pub` and `rock_laptop-id_rsa.pub`.
Make sure you don't add any extra hyphens (-) to the name as it takes the name part from the filename.  So `rock_laptop-id_rsa.pub` in the
code becomes `username = "rock_laptop-id_rsa.pub".split('-')[0]`.

These public keys referenced by the users must exist and are checked on startup.  The public keys themselves must be the copy of the original
ssh key-file from your machines.  Do not add anything to these files!  They must be single-line entries as they originally would have been.

This program reads the `authorized_keys` file located at `/home/<ssh_user>/.ssh/authorized_keys`, where `<ssh_user>` is the name referenced by
the `machine-set.csv` file as `ssh user` as shown above.

This program compares the differences, does not act if there are no changes to be made.  If there are any changes, this program will
create a new temporary `authorized_keys` file and copy it to the remote machine, overwriting the existing file of the same name located
at `/home/<ssh_user>/.ssh/authorized_keys`.

This program backs up the original `/home/<ssh_user>/.ssh/authorized_keys` to `/home/<ssh_user>/.ssh/authorized_keys.backup`.
This program will also copy the `connection-keys/id_rsa.pub` into the `authorized_keys` ensuring continued access to the server
using the user you have specified.
