Ferment
=======


Objective
---------

Create a ferm_ config for the current docker container setup. This seems useful
for automated provisioning of systems (e.g. with ansible_) which want to use
ferm_ for their firewall setup.
It is fork from original project: https://github.com/diefans/ferment with modified template for docker-ce version higher then 18


Usage
-----

Install Ferment via `pip`::

    # pip install ferment-ng


    # ferment docker --help
    Usage: ferment docker [OPTIONS] COMMAND [ARGS]...

    Options:
      -d, --docker PATH     The docker api socket.
      -c, --cidr TEXT       Docker CIDR.
      -i, --interface TEXT  Docker interface.
      --help                Show this message and exit.

    Commands:
      config

You just include a callback to ferment within your `ferm.conf`::

    # -*- shell-script -*-
    #
    #  Configuration file for ferm(1).
    #

    table filter {
        chain INPUT {
            policy DROP;

            # connection tracking
            mod state state INVALID DROP;
            mod state state (ESTABLISHED RELATED) ACCEPT;

            # allow local packet
            interface lo ACCEPT;

            # respond to ping
            proto icmp ACCEPT;

            # allow IPsec
            proto udp dport 500 ACCEPT;
            proto (esp ah) ACCEPT;

            # allow SSH connections
            proto tcp dport ssh ACCEPT;
        }
        chain OUTPUT {
            policy ACCEPT;

            # connection tracking
            #mod state state INVALID DROP;
            mod state state (ESTABLISHED RELATED) ACCEPT;
        }
        chain FORWARD {
            policy DROP;

            # connection tracking
            mod state state INVALID DROP;
            mod state state (ESTABLISHED RELATED) ACCEPT;
        }
    }

    @include '/usr/local/bin/ferment-ng docker config|';



.. _ferm: http://ferm.foo-projects.org/
.. _ansible: http://docs.ansible.com/
.. _docker: http://docs.docker.com/articles/networking/
