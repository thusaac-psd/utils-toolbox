"""Network filters for the contest playbooks."""

from ipaddress import ip_address, ip_network


def ip_in_network(address, network):
    return ip_address(address) in ip_network(network)


class FilterModule:
    def filters(self):
        return {"ip_in_network": ip_in_network}
