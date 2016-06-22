# Author : Manoj Thakkar
# Date : 06th June 2016
# This script deploy and starts a webserver on a given list of hosts (defined in hosts.json)
# All these webservers are running index.php
# It will also deploy and run nginx as load balancer for this app
# All these webserver are masked behind a nginx load balancer.
# The end user will be using the Url provided by the nginx server and the request will be
# routed to any of th webserver running behind this nginx service.
# We can scale up and scale down the webservers hosts by adding entries in
# hosts.json file.

import sys
import paramiko
import json
import logging
import socket
import os
from jinja2 import Environment, FileSystemLoader
from scp import SCPClient
from SshConnect import *


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def create_file(filename, context):
    fname = filename.replace('.template', '')
    with open(fname, 'w') as f:
        html = render_template(filename, context)
        f.write(html)


def install_nginx(vhost):
    with open('hosts.json', 'r') as fp:
        data = json.load(fp)
    PATH = os.getcwd()
    TEMPLATE_ENVIRONMENT = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(PATH, 'templates')),
        trim_blocks=False)

    host = data['nginx_config']
    name = host['cname']
    diskt = host['disk_threshold']
    override = host['override_port']
    port = host['port']
    user = host['username']
    passwd = host['password']
    install = host['install_pkg']
    ssh = SshConnect()
    ssh.connection(name, user, passwd)
    ssh1 = ssh.connection(name, user, passwd)
    scp = SCPClient(ssh1)
    scp.put('scripts/find_deleted.sh', '/tmp/find_deleted.sh')
    output = ssh.run_command('sh -c /tmp/find_deleted.sh')
    command = "df -h / | tail -n +2 | awk '{print $5}'"
    disk = ssh.run_command(command)
    logging.info("Disk usage is %s", disk)
    if int(disk.split('%')[0]) < int(diskt):
        command = "apt-get -y install " + install
        output = ssh.run_command(command)
        files = "nginx.conf.template"
        print "file name is ", files
        logging.info("changing nginx config as %s", vhost)
        context = {"hostname": name, "servers": vhost}
        create_file(files, context)
        scp.put('nginx.conf', '/etc/nginx/sites-available/default')
        scp.put('scripts/fix_iptables.sh', '/tmp/fix_iptables.sh')
        ssh.run_command("service nginx stop")
        # We can implement override port here similar to disk threshold (Not
        # implemented correctly here)
        if override:
            command = "lsof -i :" + port + \
                " | tail -n +2 | awk '{print $2}'| xargs kill -9"
            output = ssh.run_command(command)
        command = "/tmp/fix_iptables.sh " + port
        output = ssh.run_command(command)
        command = "service nginx restart"
        ssh.run_command(command)
        logging.info("nginx restart completed")
        print "nginx restart completed"
    else:
        logging.exception(
            "Disk Usgae is above threshold.Please delete unwanted data and try agian")
        exit("Installation failed on host %s", name)
    ssh1.close()


def install_apache():
    # Read apche hosts metadata from the json file
    with open('hosts.json', 'r') as fp:
        data = json.load(fp)

    for hosts in data['apache_hosts']:
        print hosts
        name = hosts['cname']
        user = hosts['username']
        passwd = hosts['password']
        diskt = hosts['disk_threshold']
        override = hosts['override_port']
        install = hosts['install_pkg']
        port = hosts['web_port']
        documentroot = hosts['documentroot']
        logging.debug("%s, %s, %s, %,s", name, user, passwd, install)
        # Command to install apache related packages
        ssh = SshConnect()
        ssh.connection(name, user, passwd)
        ssh1 = ssh.connection(name, user, passwd)
        scp = SCPClient(ssh1)
        scp.put('scripts/find_deleted.sh', '/tmp/find_deleted.sh')
        output = ssh.run_command('sh -c /tmp/find_deleted.sh')
        command = "df -h / | tail -n +2 | awk '{print $5}'"
        disk = ssh.run_command(command)
        logging.info("Disk usage is %s", disk)
        if int(disk.split('%')[0]) < int(diskt):
            command = "apt-get -y install " + install
            output = ssh.run_command(command)
            if output:
                PATH = os.getcwd()
                TEMPLATE_ENVIRONMENT = Environment(
                    autoescape=False,
                    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
                    trim_blocks=False)
                # Replace the following context from the template files
                context = {"DocumentRoot": documentroot, "ports": port}
                for files in os.listdir("templates"):
                    logging.info("file name is %s", files)
                    # Create new files from the template files after rendering
                    create_file(files, context)
                indexdoc = documentroot + "/index.php"
                ssh1 = ssh.connection(name, user, passwd)
                scp = SCPClient(ssh1)
                # Copy the newly generated files
                scp.put('ports.conf', '/etc/apache2/ports.conf')
                scp.put('apache2.conf', '/etc/apache2/apache2.conf')
                scp.put('app.conf', '/etc/apache2/sites-available/app.conf')
                scp.put('resolv.conf', '/etc/resolv.conf')
                command = 'mkdir -p ' + documentroot
                output = ssh.run_command(command)
                scp.put('index.php', indexdoc)
                output = ssh.run_command(
                    'a2dissite 000-default && a2ensite app')
                scp.put('scripts/fix_iptables.sh', '/tmp/fix_iptables.sh')
                command = "/tmp/fix_iptables.sh " + port
                logging.info("running command %s", command)
                output = ssh.run_command(command)
                output = ssh.run_command("service apache2 stop")
                # We can implement override port here similar to disk threshold
                # (Not implemented correctly here)
                if override:
                    command = "lsof -i :" + port + \
                        " | tail -n +2 | awk '{print $2}'| xargs kill -9"
                    logging.info("running command %s", command)
                    output = ssh.run_command(command)
                output = ssh.run_command('service apache2 start')
                hostconfig = hosts['cname'] + ":" + hosts['web_port']
                vhost.append(hostconfig)
                ssh1.close()
            else:
                file.write(
                    name + "::: installation failed please check output below \n")
                file.write(name + "::" + output + "\n")

        else:
            logging.exception(
                "Disk Usgae is above threshold.Please delete unwanted data and try agian")
            exit("Installation failed on host %s", name)
    print "vhost fils is ", vhost
    return vhost


if __name__ == "__main__":
    # Dump logs of installation in install.log file
    file = open('install.log', 'w')
    vhost = []
    LOG_FORMAT = '[%(asctime)s] %(message)s'
    DATE_FORMAT = '%d/%b/%Y %H:%M:%S %z'
    logging.basicConfig(level=logging.INFO,
                        format=LOG_FORMAT, datefmt=DATE_FORMAT)

    PATH = os.getcwd()
    TEMPLATE_ENVIRONMENT = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(PATH, 'templates')),
        trim_blocks=False)
    vhost = install_apache()
    install_nginx(vhost)
