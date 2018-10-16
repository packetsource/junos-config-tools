# junos-config-tools
General configuration management tools for JUNOS (requires PyEZ)

These tools provide some basic functionalities for working with test
JUNOS configurations in bulk. They make use of the Juniper-provided
PyEZ Python framework for interface with JUNOS programtically, and have
some baseline requirements:

- Key-based authentication configured on your SSH client. Typically this is
  as simple as ensuring that you have generated `~/.ssh/id_rsa` and `~/.ssh/id_rsa.pub`
  using the `ssh-keygen` utility.

- User configured within JUNOS with appropriate permissions and SSH
  key-based authentication.

```
system {
    login {
        user user {
            class super-user;
            authentication {
                ssh-rsa "ssh-rsa PUBLIC-KEY-MATERIAL-HERE user@domain.com";
            }
        }
     }
}
```

  If you have trouble cutting and pasting your SSH key to the JUNOS box,
  consider these alternatives method instead:

  - Load the public SSH key via HTTP

```
   unix:~$ python -m SimpleHTTPServer 8080

   junos# set system login user authentication load-key-file http://unix-ip-addr:8080/.ssh/id_rsa.pub
```

  - Copy the key to the JUNOS box using SCP, then use the same command with a `file://` 
    URL to load the file

## Initial Setup

- Modify the `HOSTS` array within the tools to reference your entire lab inventory.

- If necessary, modify `SSH_CONFIG` to point to an SSH configuration that defines
key files and perhaps host mappings:
```
Host vrr1
  User user
  HostName 192.168.122.1
  IdentityFile /home/adamc/junos_id_rsa
  IdentitiesOnly yes
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no
```

- The PyEZ framework does allow the use of password authentication as well,
  since it is difficult to manage password caching safely, it is not encouraged here.

## vrr-archive

`vrr-archive` is designed to either save or load a snapshot of multiple boxes allow
rapid reconfiguration if routers between configurations.  Syntax:

```
vrr-achive [load|save| [filename.tgz]
```
During a save operation, `vrr-archive` connects to the NETCONF subsystem of the JUNOS
SSH service and issues a `<get-config>` XML RPC. It writes the received XML response
to the specified filename as a gzipped TAR archive, or creates a filename based upon the
current system data and time.

During a load operation, `vrr-archive` reads the nominated gzipped TAR archive, and for
each file contained within, it uploads the XML configuration to the specified router
(providing the router is specified within the `HOSTS` array) using a `<load-config>` XML
RPC. It then commits the configuration using a `<commit-config>` XML RPC.

## vrr-config

`vrr-config` uploads a series of set/delete configuration instructions to a set of
nominated hosts, or to the set of hosts statically defined within the `HOSTS` array. Syntax:

```
vrr-config filename.txt [router1 router2 router3]
```

When invoked, `vrr-config` opens the specified file, and applies the Python string template
instantiator in order to expand some per-host variables:

- `$id` an index number of the current host, obtained by scanning the text 
  of the hostname, and perhaps useful for setting IP addresses locally.
- `$host` the text string representing the current hostname

With the resulting template expansion, it connects to each JUNOS host specified
on the command line, or the full list of hosts statically specified within the
`HOSTS` array, and uses the private configuration load option of the `<open-configuration>`
XML RPC to upload the configuration, before committing it. (The private load option is used
in case the configuration snippet contains commit errors which will simply accumulate over
multiple attempts to specify the correct configuration).
