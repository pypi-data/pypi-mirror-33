# check_crmresource

Nagios plugin to check status of a CRM resource


## Usage

```
usage: check_crmresource.py [-h] [-r RESOURCE] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -r RESOURCE, --resource RESOURCE
                        Name of the resource that is beeing tested
  -v, --verbose         Increase output verbosity (use up to 3 times)

```

## Requirements
- nagiosplugin (https://bitbucket.org/flyingcircus/nagiosplugin)

- sudo  
  The user running the plugin (usually `nagios` or `icinga`) needs permissons to run `crm_resource --list` as root user. An example sudoers file (e.g. `/etc/sudoers.d/crm_resource`) could look like this:  
  ```
  Cmnd_Alias CRMRESOURCE = /usr/sbin/crm_resource --list
  icinga ALL=(ALL) NOPASSWD: CRMRESOURCE
  Defaults!CRMRESOURCE !requiretty
  ```

## Acknowlegments

This plugin borrows some ideas from various other similar plugins. However most of these don't handle corner cases (such as a partition with quorum but failed resources) correctly or report 'OK' states erroneously if resources are not started. This plugin aims to fix those shortcomings.
