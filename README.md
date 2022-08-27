## Simple machine ssh manager

Use a definitions file `machine-set.csv` and a set of known public keys
located in `public-keys` to manage access to a series of machines.

### machine-set.csv format

An example is shown below 

| machine ip or hostname | ssh port | ssh user | ssh keys / user names  |
|------------------------|----------|----------|------------------------|
| test01-app01           | 22       | simsage  | rock, rock_laptop      |

The *hardest* part is gathering the existing public keys.  Copy each key from any/all machines you need and prepend each key with a name.
The above example thus assumes there is a machine called `test01-app01` that is accessible over ssh using a user-account called `simsage`.
For this to work you should be able to run `ssh simsage@test01-app01` and connect.  Port 22 in this case is the default ssh port and doesn't
change anything.

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

It does not backup the original `/home/<ssh_user>/.ssh/authorized_keys`.  Please be careful how you use this file, and test it first on a machine of low importance to you
where you can easily re-establish contact if the ssh shell fails.  I have tested this program, and do use it myself.  Please make
sure however that it works the way you think it works to avoid losing access to any of your remote machines.

