#!/usr/bin/python3
# Copyright (c) 2022, Rock de Vocht
import os
from os import listdir
from os.path import isfile, join, exists
import uuid

# any key we can't identify will get this username
unknown_user = "UNKNOWN"
# default ssh port as a string
default_port = "22"


# read the data from inside machine-set.csv
def read_machine_set_csv():
    # the declarative set of what we want
    machine_dict = dict()
    # read the CSV file and process it
    with open("machine-set.csv", "rt") as reader:
        for line in reader:
            line = line.strip()
            if line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) == 6:
                ssh_machine = parts[0].strip()
                ssh_port = parts[1].strip()
                ssh_access_user = parts[2].strip()
                ssh_private_key_path = parts[3].strip()
                ssh_public_key_path = parts[4].strip()
                if not exists(ssh_private_key_path):
                    raise ValueError("file does not exist: {}".format(ssh_private_key_path))
                if not exists(ssh_public_key_path):
                    raise ValueError("file does not exist: {}".format(ssh_public_key_path))
                user_list = []
                csv_users_list = parts[5].strip().split(",")
                for ssh_user in csv_users_list:
                    ssh_user = ssh_user.strip()
                    if len(ssh_user) > 0:
                        user_list.append(ssh_user)
                machine_dict[ssh_machine] = dict()
                machine_dict[ssh_machine]["user"] = ssh_access_user
                machine_dict[ssh_machine]["port"] = ssh_port
                machine_dict[ssh_machine]["allowed_user_list"] = user_list
                machine_dict[ssh_machine]["private_key"] = ssh_private_key_path
                machine_dict[ssh_machine]["public_key"] = ssh_public_key_path

    return machine_dict


# get a list of authorized users from a remote server from the authorized_users file on that server
def get_authorized_users(ssh_user, ssh_cert_path, ssh_server, ssh_port):
    ssh_key_list = []  # list of users found on the machine
    exec_str = "ssh -o \"StrictHostKeyChecking no\" "
    if ssh_port != "22":  # default port doesn't need to be addressed
        exec_str += "-p {} ".format(ssh_port)
    exec_str += "-i {} {}@{} ".format(ssh_cert_path, ssh_user, ssh_server)
    exec_str += "'cat /home/{}/.ssh/authorized_keys'".format(ssh_user)
    try:
        # execute the command and get the list of users
        result = os.popen(exec_str)
        output = result.read()
        if len(output.strip()) == 0:
            print("error executing: {}".format(exec_str))
            exit(-1)
        # split across new-lines
        for file_line in output.split('\n'):
            file_line = file_line.strip()
            # look for anything starting with ssh-ras, our public keys
            if file_line.startswith("ssh-rsa "):
                # just take the key/identifier part
                ssh_key_list.append(file_line.strip().split(" ")[1])
        return ssh_key_list
    except OSError:
        print("error executing: {}".format(exec_str))
        exit(-1)  # failed - can't continue


# backup the existing authorized keys in the same .ssh on the remote server as authorized_keys.backup
def backup_authorized_keys(ssh_user, ssh_cert_path, ssh_server, ssh_port):
    port_str = ""  # set the port if it isn't the default one
    if ssh_port != "22":  # default port doesn't need to be addressed
        port_str = "-p {}".format(ssh_port)
    exec_str = "ssh -i {} {} -o \"StrictHostKeyChecking no\" {}@{} \"cp /home/{}/.ssh/authorized_keys " \
               "/home/{}/.ssh/authorized_keys.backup\""\
            .format(ssh_cert_path, port_str, ssh_user, ssh_server, ssh_user, ssh_user)
    # execute the command to copy the new authorized_keys file to this machine
    os.system(exec_str)


# get a list of authorized users from a remote server from the authorized_users file on that server
def copy_authorized_keys(ssh_user, ssh_cert_path, ssh_server, ssh_port, authorized_keys_filename):
    port_str = ""  # set the port if it isn't the default one
    if ssh_port != "22":  # default port doesn't need to be addressed
        port_str = "-P {}".format(ssh_port)
    exec_str = "scp -i {} -o \"StrictHostKeyChecking no\" {} {} {}@{}:/home/{}/.ssh/authorized_keys"\
        .format(ssh_cert_path, port_str, authorized_keys_filename, ssh_user, ssh_server, ssh_user)
    # execute the command to copy the new authorized_keys file to this machine
    os.system(exec_str)


# get the known keys from the public-keys/ folder here
# so we can recognize these keys in our machine inventory
def get_known_keys():
    key_user_dict = dict()  # key -> user-name
    # from the public-keys folder, keys must end in .pub
    # the part of the filename before the first hyphen is the name of the key
    # e.g. ben-id_rsa.pub is a valid filename for a user called "ben"
    folder = "public-keys"
    list1 = [(join(folder, f), f.split("-")[0]) for f in listdir(folder) if
             isfile(join(folder, f)) and f.endswith("-id_rsa.pub")]
    for file_path, key_user in list1:
        with open(file_path, "rt") as reader:
            # key-part -> user-name
            full_key = reader.read().strip()
            key_part = full_key.split(" ")[1]
            key_user_dict[key_part] = (key_user, full_key)
    return key_user_dict


# combine our existing/known users with the ones found on a machine
# and return a list of the users found inside the authorized_users file
def get_users_on_machine(authorized_user_key_list, local_key_to_user_dict):
    users_on_machine = []
    for key in authorized_user_key_list:
        if key in local_key_to_user_dict:
            known_user = local_key_to_user_dict[key]
            users_on_machine.append(known_user)
        else:
            users_on_machine.append(unknown_user)
    return users_on_machine


# create a diff set between two lists, these are returned as a tuple of
# two lists, the first the items to remove, the second, the items to add
def get_difference(current, allowed):
    # create a fast lookup for the current items
    current_set = set()
    for item in current:
        current_set.add(item)
    allowed_set = set()
    for item in allowed:
        allowed_set.add(item)
    remove_list = []
    for item in current:
        if item not in allowed_set:
            remove_list.append(item)
    add_list = []
    for item in allowed:
        if item not in current_set:
            add_list.append(item)
    return remove_list, add_list


if __name__ == '__main__':
    # first get all the local keys, our data-set of known public keys
    known_key_set = get_known_keys()
    if len(known_key_set) == 0:
        print("no public keys found in public-keys/, cannot continue")
        exit(-1)
    # lookup keys by username (i.e. the inverse of key_to_user_dict)
    user_to_key_dict = dict()
    key_to_user_dict = dict()
    for key in known_key_set:
        user, full_key = known_key_set[key]
        user_to_key_dict[user] = full_key
        key_to_user_dict[key] = user

    # read the data
    machine_set = read_machine_set_csv()
    # check we have data
    if len(machine_set) == 0:
        print("machine-set empty, nothing to check")
        exit(-1)

    # check each of the "allowed_user_list" user-names are in the key-to-user dict
    # so we can reliably replace them
    for machine in machine_set:
        machine_record = machine_set[machine]  # machine is the name/host of the remote machine to access
        user_set = machine_record["allowed_user_list"]  # the users we allow must have keys!
        for user in user_set:
            if user not in user_to_key_dict:
                raise ValueError("unknown user {} in the 'allowed_user_list' of machine {}".format(user, machine))

    # now go through each of the machines and update authorized_keys as required
    for machine in machine_set:
        machine_record = machine_set[machine]  # machine is the name/host of the remote machine to access
        machine_user = machine_record["user"]  # the login for this machine
        if "port" in machine_record:
            machine_port = str(machine_record["port"])  # the login for this machine
        else:
            machine_port = default_port  # default port is ued if not in the record
        private_key_file_location = machine_record["private_key"]
        # store the list of keys seen on this machine in its record
        machine_keys_list = get_authorized_users(machine_user, private_key_file_location, machine, machine_port)
        # and match this list with the list of existing users locally to get a second
        # list of the same size translating each key to a user
        current_user_list = get_users_on_machine(machine_keys_list, key_to_user_dict)
        allowed_user_list = machine_record["allowed_user_list"]

        # process each machine and copy a new authorized_keys file if needed
        remove_list, add_list = get_difference(current_user_list, allowed_user_list)

        if len(remove_list) > 0 or len(add_list) > 0:
            print("machine {}".format(machine))
            print("    existing users: {}".format(current_user_list))
            print("    allowed users: {}".format(allowed_user_list))
            print("    users to remove: {}, users to add: {}".format(remove_list, add_list))

            # read the public key
            public_key_path = machine_record["public_key"]
            with open(public_key_path, "rt") as reader:
                public_key = reader.read().strip()
                if len(public_key) == 0:
                    raise ValueError("invalid public key (empty): {}".format(public_key_path))

            # create a new authorized_keys file for the users that are allowed
            authorized_users_file = []
            has_public_key = False
            for user in allowed_user_list:
                allowed_key = user_to_key_dict[user].strip()
                authorized_users_file.append("# {}".format(user))
                authorized_users_file.append(allowed_key)
                if allowed_key == public_key:
                    has_public_key = True
                authorized_users_file.append("")

            # and add the public key as an accessor so this program retains access if we don't already have it
            if not has_public_key:
                authorized_users_file.append("# connection key ssh key")
                authorized_users_file.append(public_key)
                authorized_users_file.append("")

            # create a temp file to copy across
            file_content = '\n'.join(authorized_users_file)
            temp_filename = "authorized_keys_{}".format(uuid.uuid4())
            with open(temp_filename, 'wt') as writer:
                writer.write(file_content)
            # backup the existing authorized_keys first
            backup_authorized_keys(machine_user, private_key_file_location, machine, machine_port)
            # and copy it to the remote machine - replacing the old keys
            copy_authorized_keys(machine_user, private_key_file_location, machine, machine_port, temp_filename)
            # remove the temp file created after scp (copy)
            os.remove(temp_filename)

        else:
            print("machine {}: no change, user with access: {}".format(machine, allowed_user_list))
