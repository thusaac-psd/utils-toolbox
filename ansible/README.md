# Contest Ansible playbooks

Run the examples from this directory so Ansible loads `ansible.cfg`. For
another working directory, set `ANSIBLE_CONFIG` to its absolute path. The
controller needs Ansible and `community.general`. Account management,
Bluetooth and UFW assume Debian or Ubuntu with Python 3 and systemd.

```sh
ansible-galaxy collection install -r requirements.yml
ansible-inventory -i inventories/site.yml --graph
ansible-playbook -i inventories/site.yml playbooks/discover.yml --limit contestants
```

Copy `inventories/example.yml` and the example `group_vars/contestants.yml`
into your site inventory directory. Set the SSH user and replace the example
addresses, accounts and networks. Keep contestant machines in `contestants`
and judge servers in `judgehosts`. Use `--limit seat-01` to start with one
machine. SSH host key verification is enabled. After a rebuild, verify the new
fingerprint through a trusted source and refresh `known_hosts`. If your sudo
configuration requires a TTY, set `ansible_pipelining: false` on those hosts.

| Playbook | Use |
| --- | --- |
| `discover.yml` | Probe selected inventory hosts, export reachable hosts and report failures. |
| `ping.yml` | Run the same probe and write only the report. |
| `create-user.yml` | Create an account with its initial password. Existing accounts are skipped. |
| `remove-user.yml` | Remove an account and its home directory. Missing accounts are skipped. |
| `remove-user-and-files.yml` | Also remove files owned by the account under the standard temporary, runtime and spool directories. |
| `install-vscode-extensions.yml` | Install missing extensions for an existing account on each host. Run while the Marketplace is reachable, before restricting outbound traffic. |
| `setup-netrc.yml` | Write per-host DOMjudge credentials to an existing account's actual home directory. |
| `setup-local-dns.yml` | Map one hostname in `/etc/hosts`, preserving other aliases and comments. |
| `disable-bluetooth.yml` | Stop, disable and mask Bluetooth where its service is installed. |
| `enable-ufw.yml` | Apply the contest firewall policy one selected host at a time. |
| `disable-ufw.yml` | Disable UFW on selected hosts where it is installed. |
| `send-file.yml` | Copy a file between absolute paths. Supply `dest_owner` and a quoted `dest_mode` when needed. The default mode is `0644`. |
| `run-command.yml` | Run a privileged shell command on selected contestant hosts and show stdout and stderr. |
| `fix-domjudge.yml` | Configure API credentials and daemon accounts on source-built judgehosts that already have upstream sudoers configured. |

## Discovery output

The default controller paths are `ansible/discovered.ini` and
`ansible/unreachable_hosts.log`. Override them with absolute
`discovered_inventory_path` and `unreachable_report_path` values. The export
includes reachable host names, basic connection settings and the original
`contestants` and `judgehosts` memberships. Use the site inventory alongside
the export to retain its variables and credentials. For example, where
`reachable` is reserved for the export:

```sh
ansible-playbook -i inventories/site.yml -i discovered.ini playbooks/create-user.yml --limit 'contestants:&reachable'
```

## Accounts and credentials

List removable accounts in `contest_managed_accounts` and add administrative
accounts to `contest_protected_accounts`. The removal scripts independently
check the UID and SSH login before changing anything.

Give `setup-netrc.yml` an absolute controller-side CSV path. Use the columns
`ip,oj_username,oj_password`, one row per host. The first column matches
the inventory name first, then `ansible_host` when set. Set `netrc_host_key`
to select one specific CSV key for a host. Keep credentials in a
local restricted file or Ansible Vault.

For judgehosts, define `domjudge_run_ids` per host and supply the API URL
and password interactively or from Vault. The playbook verifies that upstream
sudoers permits `runguard` before restoring its regular executable permissions.
The previous local chroot ownership workaround depends on the DOMjudge release
and site layout.

## Firewall

Set `ufw_management_network` to the CIDR or address containing the current
controller or SSH jump host, as seen by each contestant machine. The playbook
uses the port of that SSH connection and checks a fresh connection before moving
on. List permitted outbound destinations in `ufw_outbound_rules` as
`{ip, port, proto}` entries. Protocol defaults to TCP. Specify UDP explicitly
for services that require it. Entries match IP addresses or CIDRs.

Unrelated UFW rules are preserved. Review existing rules for broader allows
before using the host as an isolated contestant machine. To retire previously
managed outbound permits, list their exact parameters in
`ufw_retired_outbound_rules`. For rules created by the earlier playbook without
a protocol, specify `proto: any` in the retirement list. An SSH management
network change also requires removing the previous management permit.
