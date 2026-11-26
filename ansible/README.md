# Contest Ansible playbooks

Run the commands from this directory so Ansible loads `ansible.cfg`. The
playbooks assume Ubuntu contestant machines and judgehosts installed from
source under `/opt/domjudge`.

```sh
ansible-galaxy collection install -r requirements.yml
cp -R inventories/example inventories/site   # ignored by Git
# Edit inventories/site/hosts.yml and inventories/site/group_vars/contestants.yml.
ansible-playbook -i inventories/site/hosts.yml playbooks/discover.yml
```

Keep contestant machines in `contestants` and judge servers in `judgehosts`.
Use `--limit seat-01` to try a playbook on one machine first.

| Playbook | Use |
| --- | --- |
| `discover.yml` | Write `discovered.ini` with a `reachable` group and `unreachable_hosts.log`. |
| `create-user.yml` | Create an account. An existing account keeps its password. |
| `remove-user.yml` | Kill the account's processes, delete its files in `/tmp`, `/var/tmp`, `/var/spool` and `/dev/shm`, then remove it with its home directory. |
| `install-vscode-extensions.yml` | Install missing extensions for a user. Run before `enable-ufw.yml` blocks the Marketplace. |
| `setup-netrc.yml` | Write per-host DOMjudge credentials to a user's `~/.netrc`. |
| `setup-local-dns.yml` | Map a hostname in `/etc/hosts`. A line that already lists the name is replaced as a whole. |
| `disable-bluetooth.yml` | Stop and mask Bluetooth. |
| `enable-ufw.yml` | Replace all UFW rules with the contest policy, one host at a time. |
| `disable-ufw.yml` | Disable UFW. |
| `send-file.yml` | Copy a file. Pass `-e dest_owner=...` or `-e dest_mode=...` when needed. |
| `run-command.yml` | Run a shell command as root and show its output. |
| `configure-judgehost.yml` | Write the API credentials, drop the SUID bit from `runguard` and create the run accounts. |

## Running on reachable machines only

Playbooks continue past offline machines, except `enable-ufw.yml`, which stops
at the first failure. Limit a run to the machines found by `discover.yml`:

```sh
ansible-playbook -i inventories/site/hosts.yml -i discovered.ini playbooks/enable-ufw.yml --limit 'contestants:&reachable'
```

## Variables

- `contest_managed_accounts`: the only accounts `remove-user.yml` may remove.
  It also refuses system accounts and the SSH login Ansible uses.
- `ufw_management_network`: CIDR allowed to SSH in. It must contain the address
  Ansible connects from, or the playbook stops before touching the firewall.
- `ufw_outbound_rules`: `{ip, port, proto}` destinations contestants may reach.
  `proto` defaults to `tcp`.
- `domjudge_run_ids`: judge daemon numbers per judgehost, e.g. `[2, 3]` for
  `domjudge-run-2` and `domjudge-run-3`.

`setup-netrc.yml` reads a controller-side CSV with the columns
`ip,oj_username,oj_password`. Rows are matched against each host's
`ansible_host`, or its inventory name when `ansible_host` is unset. A host
without a row fails. Keep the CSV out of the repository.
