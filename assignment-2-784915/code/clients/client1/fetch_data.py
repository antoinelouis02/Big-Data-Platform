import urllib.request
from os import listdir, path, system
import argparse
import json


def get_constraints(username, password):
    """
    Make a request to mysimdbp-server to get the constraints of client.
    """
    # Request
    fp = urllib.request.urlopen("http://localhost:5000/constraints/{}/{}".format(username, password))

    # Read response
    encodedContent = fp.read()
    decodedContent = encodedContent.decode("utf8")

    # Close the server connection and return result
    fp.close()
    return decodedContent


def get_files_to_fetch(constraints, indir_path):
    """
    Check files that can be fetched into mysimbdp-server.
    """
    # Get different constraints
    constraints = json.loads(constraints)
    allowed_formats = tuple(constraints["allowed_file_format"])
    max_size = constraints['max_file_size']
    max_nb = constraints['max_nb_files']
    files_to_fetch = []

    # Get all files of input directories with allowed extensions
    files = [f for f in listdir(indir_path) if path.isfile(path.join(indir_path, f)) and f.endswith(allowed_formats)]
    print(files)
    
    # While we do not exceed max number of files, get files to fetch
    while len(files_to_fetch) < max_nb and files:
        # Pop a file out of the list
        f = files.pop(-1)

        # Check max size
        f_size = path.getsize(path.join(indir_path, f)) /1024
        if f_size > max_size:
            print("{} is heavier than maximum file size allowed of {} KB".format(f, max_size))
            continue

        # Append file to list to fetch if not already in the list
        f_path = path.join(indir_path, f)
        if f_path not in files_to_fetch:
            files_to_fetch.append(f_path)

    return files_to_fetch


def fetch(files):
    """
    Fetch allowed files to mysimbdp-server.
    """
    for path in files:
        system("docker cp " + path + " server:/server/dir1/files/")
        print('{} has been fetched to mysimbdp-server.'.format(path))


def parse_arguments():
    """
    :return: the different arguments of the command line.
    """
    parser = argparse.ArgumentParser("Init the Cassandra database.")
    parser.add_argument("--username", type=str, default='john_doe',
                        help="Username of client 1. Default is john_doe.")
    parser.add_argument("--password", type=str, default='1234',
                        help="Password of client 1. Default is 1234.")
    parser.add_argument("--indir", type=str, default='client-input-directory/',
                        help="Input directory of client 1. Default is 'client-input-directory.")
    args, _ = parser.parse_known_args()
    return args


if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()

    # Get constraints of client
    constraints = get_constraints(args.username, args.password)
    print(constraints)
    
    # Get files to fetch according to the constraints
    full_path = path.dirname(path.realpath(__file__))
    indir_path = path.join(full_path, args.indir)
    files = get_files_to_fetch(constraints, indir_path)
    print(files)

    # Fetch data
    fetch(files)
