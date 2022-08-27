## Simple machine ssh manager

Use a definitions file `machine-set.csv` and a set of known public keys
located in `public-keys` to manage access to a series of machines.

### machine-set.csv format

An example is shown below 

| machine ip or hostname | ssh port | ssh user | ssh keys / user names   |
| --- | --- | --- |-------------------------|
| test01-app01 | 22 | simsage | rock, ingo, rock_laptop |

The `hardest` part is gathering the existing public keys.  Copy each 
key from any/all machines you need and prepend each key with a name.

e.g. the public key from a machine called `jumphost` should be put in
`public-keys/` as `jumphost-id_rsa.pub`

