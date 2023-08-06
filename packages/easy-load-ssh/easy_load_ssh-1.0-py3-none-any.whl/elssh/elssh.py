import subprocess, sys, getpass, click

@click.command()
@click.option('--username', default=getpass.getuser())
@click.option('--domain', default='mines.edu')
@click.option('--host-range', default='ch215l-[01-16].mines.edu', help='Range of hosts to search')
def cli(username, domain, host_range):
    def host_sort_key(host):
        return host[1][2]

    def least_busy_host_name(name_load_dict):
        name, shortest_load_avgs = sorted(name_load_dict.items(), key=host_sort_key)[0]
        return name

    cmd_str = "pdsh -R ssh -l {} -w {} -f 1 'uptime' 2>/dev/null".format(username, host_range)
    result = subprocess.run(cmd_str, shell=True, stdout=subprocess.PIPE)
    host_str = result.stdout.decode('utf-8')

    if not host_str:
        sys.exit('No hosts were returned with the supplied pattern')

    name_load_dict = {}
    for line in host_str.splitlines():
        name, *stuff, str_load_avgs = line.split(':')
        num_load_avgs = list(map(lambda x: float(x.strip()), str_load_avgs.split(',')))
        name_load_dict[name] = num_load_avgs

    candidate_host = least_busy_host_name(name_load_dict)
    subprocess.run(['ssh', '{}@{}.{}'.format(username, candidate_host, domain)])
