"""Network input validation and hosts-file updates for the contest playbooks."""

from ipaddress import ip_address, ip_network
import re

from ansible.errors import AnsibleFilterError


def _matches_address_or_network(value):
    try:
        ip_network(value)
    except (TypeError, ValueError):
        return False
    return True


def _address_in_network(address, network):
    try:
        return ip_address(address) in ip_network(network)
    except (TypeError, ValueError) as error:
        raise AnsibleFilterError(str(error)) from error


def _update_hosts_file(contents, address, hostname):
    address = str(ip_address(address))
    if not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9.])?", hostname):
        raise AnsibleFilterError("Expected a single hostname to map in /etc/hosts.")

    target = hostname.rstrip(".").lower()
    lines = []
    found = False
    for line in contents.splitlines(keepends=True):
        body, marker, comment = line.rstrip("\r\n").partition("#")
        fields = body.split()
        names = fields[1:]
        remaining = [name for name in names if name.rstrip(".").lower() != target]
        if len(names) == len(remaining):
            lines.append(line)
        elif not found and fields[0] == address and len(names) == len(remaining) + 1:
            lines.append(line)
            found = True
        elif remaining:
            lines.append(" ".join([fields[0], *remaining]) + (" " + marker + comment if marker else "") + "\n")
        elif marker:
            lines.append(marker + comment + "\n")

    if not found:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines.append("\n")
        lines.append(f"{address} {hostname}\n")
    return "".join(lines)


class FilterModule:
    def filters(self):
        return {
            "contest_ip_network": _matches_address_or_network,
            "contest_ip_in_network": _address_in_network,
            "contest_update_hosts_file": _update_hosts_file,
        }
