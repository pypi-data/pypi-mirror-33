import sh
import json
import uuid
from time import sleep

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


def get_git_branch():
    """Retrieve current git branch name of calling repo

    Returns:
        str: current git branch name
    """

    git = sh.git.bake(_cwd='.')
    return git('rev-parse', '--abbrev-ref', 'HEAD')


def get_osa_version_tuple():
    """Get tuple of OpenStack version (code_name, major_version) as raw
    strings.

    This data is based on the git branch of the test suite being executed
    Returns:
        tuple: (code_name, major_version) as raw strings of OpenStack version
    """

    cur_branch = get_git_branch()

    if cur_branch in ['newton', 'newton-rc']:
        return (r'Newton', r'14')
    elif cur_branch in ['pike', 'pike-rc']:
        return (r'Pike', r'16')
    elif cur_branch in ['queens', 'queens-rc']:
        return (r'Queens', r'17')
    elif cur_branch == 'master-rc':
        return (r'Queens', r'17')
    else:
        return (r'\w+', r'\d+')


def get_id_by_name(service_type, service_name, run_on_host):
    """Get the id associated with name

    Args:
        service_type (str): The OpenStack object type to query for.
        service_name (str): The name of the OpenStack object instance to query
                            for.
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.

    Returns:
        string: Id of Openstack object instance. None if result not found.
    """
    cmd = "{} openstack {} show \'{}\' -f json'".format(utility_container,
                                                        service_type,
                                                        service_name)
    output = run_on_host.run(cmd)
    try:
        result = json.loads(output.stdout)
    except ValueError:
        return

    if 'id' in result:
        return result['id']
    else:
        return


def create_bootable_volume(data, run_on_host):
    """Create a bootable volume using a json file

    Args:
        data (dictionary): Dictionary in the following format:
                           { 'volume': { 'size': '',
                                         'imageref': '',
                                         'name': '',
                                         'zone': '',
                                       }
                           }
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.
    """

    volume_size = data['volume']['size']
    imageRef = data['volume']['imageRef']
    volume_name = data['volume']['name']
    zone = data['volume']['zone']

    cmd = "{} openstack volume create \
           --size {} \
           --image {} \
           --availability-zone {} \
           --bootable {}'".format(utility_container, volume_size, imageRef,
                                  zone, volume_name)
    run_on_host.run_expect([0], cmd)


def openstack_name_list(name, run_on_host):
    """Get a list of OpenStack object instances of given type.

    Args:
        name (str): The OpenStack object type to query for.
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.

    Returns:
        string: List of OpenStack object instances in table format.
    """
    cmd = "{} openstack {} list'".format(utility_container, name)
    output = run_on_host.run(cmd)
    return output.stdout


def delete_volume(volume_name, run_on_host):
    """Delete OpenStack volume

    Args:
        volume_name (str): OpenStack volume identifier (name or id).
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.

    Raises:
        AssertionError: If operation unsucessful.
    """
    volume_id = get_id_by_name('volume', volume_name, run_on_host)
    cmd = "{} openstack volume delete --purge {}'".format(utility_container,
                                                          volume_id)
    output = run_on_host.run(cmd)
    assert volume_name not in output.stdout


def parse_table(ascii_table):
    """Parse an OpenStack ascii table

    Args:
        ascii_table (str): OpenStack ascii table.

    Returns:
        list: List of column headers from table.
        list: List of column rows from table.
    """
    header = []
    data = []
    for line in filter(None, ascii_table.split('\n')):
        if '-+-' in line:
            continue
        if not header:
            header = filter(lambda x: x != '|', line.split())
            continue
        data.append([''] * len(header))
        splitted_line = filter(lambda x: x != '|', line.split())
        for i in range(len(splitted_line)):
            data[-1][i] = splitted_line[i]
    return header, data


def generate_random_string(string_length=10):
    """Generate a random string of specified length string_length.

    Args:
        string_length (int): Size of string to generate.

    Returns:
        string: Random string
    """
    random_str = str(uuid.uuid4())
    random_str = random_str.upper()
    random_str = random_str.replace("-", "")
    return random_str[0:string_length]  # Return the random_str string.


def get_expected_value(service_type, service_name, key, expected_value,
                       run_on_host, retries=10):
    """Getting an expected status after retries

    Args:
        service_type (str): The OpenStack object type to query for.
        service_name (str): The name of the OpenStack object instance to query
                            for.
        key (str): The OpenStack object instance parameter to check against.
        expected_value (str): The expected value for the given key.
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.
        retries (int): The maximum number of retry attempts.

    Returns:
        boolean: Whether the expected value was found or not.
    """
    for i in range(0, retries):
        cmd = "{} openstack {} show \'{}\' -f json'".format(utility_container,
                                                            service_type,
                                                            service_name)
        output = run_on_host.run(cmd)
        result = json.loads(output.stdout)

        if key in result:
            if result[key] == expected_value:
                return True
            else:
                sleep(6)
        else:
            return False

    return False


def delete_instance(instance_name, run_on_host):
    """Delete OpenStack instance

    Args:
        instance_name (str): OpenStack server identifier (name or id).
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.

    Raises:
        AssertionError: If operation unsucessful.
    """
    instance_id = get_id_by_name('server', instance_name, run_on_host)
    cmd = "{} openstack server delete {}'".format(utility_container,
                                                  instance_id)
    output = run_on_host.run(cmd)
    assert instance_name not in output.stdout
