[![Build Status](https://travis-ci.org/arbulu89/shaptools.svg?branch=master)](https://travis-ci.org/arbulu89/shaptools)
[![Coverage Status](https://coveralls.io/repos/github/arbulu89/shaptools/badge.svg?branch=master)](https://coveralls.io/github/arbulu89/shaptools?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/a6ad5be09f1a9cf19321/maintainability)](https://codeclimate.com/github/arbulu89/shaptools/maintainability)

# SHAPTOOLS

Project created to expose an API with the SAP HANA platform major functionalities.
The main idea is to have an easy and friendly environment to deploy and configure
the SAP HANA environment and enable System replication feature.

Example of how to use the package:

```python
from shaptools import hana

h = hana.HanaInstance('prd', '00', 'Qwerty1234')

if not h.is_installed():
  conf_file = hana.HanaInstance(.create_conf_file(
    '/sap_inst/51052481', '/home/myuser/hana.conf', 'root', 'root')
  hana.HanaInstance(.update_conf_file(
    conf_file, sid='PRD', password='Qwerty1234', system_user_password='Qwerty1234')
  hana.HanaInstance(.install('/sap_inst/51052481', conf_file, 'root', 'root')

if not h.is_running():
    h.start()

state = h.get_sr_state()

h.create_user_key(
  'backupkey', 'hana01:30013', 'SYSTEM', 'Qwerty1234', 'SYSTEMDB')
h.create_backup('backupkey', 'Qwerty1234', 'SYSTEMDB', 'backup')
h.sr_enable_primary('NUREMBERG')
```

## Installation

To install the **shaptools** package run the pip command:

    pip install .

To install it in a development state run:

    pip install -e .

## Dependencies

List of dependencies are specified in the ["Requirements file"](requirements.txt). Items can be installed using pip:

    pip install -r requirements.txt

## License

See the [LICENSE](LICENSE) file for license rights and limitations.

## Author

Xabier Arbulu Insausti (xarbulu@suse.com)

## Reviewers

*Pull request* preferred reviewers for this project:
- Xabier Arbulu Insausti (xarbulu@suse.com)
