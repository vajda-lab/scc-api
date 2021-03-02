#!/usr/bin/env python

import io, os, paramiko
from scc_vars import CONNECTION_CONFIG


local_pdb_path = "/home/awake/Dropbox/Vajda_Lab/Keseru/gpcrs/raw_pdbs/domain_split/"
local_runme_path = "/home/awake/ftplus/dev/"

remote_path = "/projectnb/docking/awake/testing/"

pdb_file = "5TZRAa.pdb"
runme_file = "run_atlas.py"


def get_client(conn_config):
    """
    Returns a redis connection object
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        conn_config["host"],
        username=conn_config["login"],
        password=conn_config["password"],
    )
    return client


def send_file(local_path, remote_path, file):
    """
    Transmit a file to a remote host via SSH

    We transmit the indicated file to the target location. Any errors
    are simply passed along.

    :param source: Name of file to send to indicated host.
    :param dest: Full path on host to send file.

    :raise: Exception output obtained from secure transmission, if any.
    """
    source = local_path + file
    dest = remote_path + file
    client = get_client(CONNECTION_CONFIG)
    sftp = client.open_sftp()
    sftp.put(source, dest)
    sftp.close()
    client.close()


def check_file_exists(remote_path, file):
    """

    :param dest:
    :return:
    """
    client = get_client(CONNECTION_CONFIG)
    stdin, stdout, stderr = client.exec_command(
        "test -e {}{} && echo exists".format(remote_path, file)
    )
    errs = stderr.readline()
    if errs:
        raise Exception(
            "Failed to check existence of {}{}: {}".format(remote_path, file, errs)
        )

    if stdout.read().strip().decode("utf-8") == "exists":
        return True


def edit_runme(remote_path, pdb_file, runme_file):

    client = get_client(CONNECTION_CONFIG)
    stdin, stdout, stderr = client.exec_command(
        "cd {} ; sed -i -e 's/replace1/{}/g' {}{}".format(
            remote_path, pdb_file, remote_path, runme_file
        )
    )


def run_runme(remote_path):
    client = get_client(CONNECTION_CONFIG)
    stdin, stdout, stderr = client.exec_command(
        "qsub {}run_atlas.py".format(remote_path)
    )


def retrieve_files():
    pass


if __name__ == "__main__":

    # create a temporary scc directory called whatever job id is

    # copy a pdb file to scc
    # send_file(local_pdb_path, remote_path, pdb_file)

    # check if pdb file was transferred
    # if check_file_exists(remote_path, pdb_file):
    #     print('true')
    # else:
    #     print('false')

    # copy a runme file to scc
    send_file(local_runme_path, remote_path, runme_file)

    # check if pdb file was transferred
    if check_file_exists(remote_path, runme_file):
        print("true")
    else:
        print("false")


# run atlas
#     1. create a runme file
#     edit_runme(remote_path, pdb_file, runme_file)
#     print('done')

#     2. run runme file
#     run_runme(remote_path)

#   3. retrieve job
