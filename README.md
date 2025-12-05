# HDCLI
A commandline wrapper for accessing HDTools. Has script integration, designed to be an all in one tool for HDTools automation and usage. Can also prove useful while developing new scripts.

## Setup
Install python (apt/download etc.) Note on debian based distros you need: `python3` `python3-venv` `python3-pip`\
`python -m venv .venv`\
`pip install -r requirements.txt`

## Usage
`hdcli.py -h` for addtional help/usage information. Commands themselves also have additonal help menus i.e. `hdcli.py {COMMAND} -h`.\
**This tool has a few modes:**
### Command Mode
`hdcli.py {COMMAND}`
You can use a variety of commands directly from the commandline to get text and json output. Useful for batch jobs (input file) or automations.

### CLI Mode
`hdcli.py cli`
Creates an interactive command line to access HDTools in. Similar but simplistic compared to browser functionality.

### Example Usages
Note: All of these commands can be run with any number/format of input for usernames, either via the input flag `-i {FILE}` or on the command line.

#### `hdcli.py search {username}`
Returns basic information about the user, including: ZID, name, identity type, suffix, primary affiliation, affiliations, usernames, XID, CUID, employee ID, and VIP status.
Example output:
```js

```

#### `hdcli.py reset {username}`
Resets the user's password and returns the new password. Adds a description noting that the password was reset by IT Security at the current date and time.
Example output:
```js

```

`hdcli.py department {username}`
Returns the user's department(s). Example output:
    dharve3:Experiential Education;CCIT Customer Support Services

`hdcli.py supervisor {username}`
Returns the user's supervisor(s). Example output:
    dharve3:Nunamaker,Troy D;Price,Brian A

`hdcli.py abroad {username}`
Returns a dictionary storing the user's abroad status, with true indicating the 
user is abroad and false indicating the user is local. Example output:
    {'dharve3': False, 'lilahs': False}

`hdcli.py active {username}` 
Returns a list displaying whether the user's account is active or not, with true indicating an
active account and false indicating an inactive account. Example output:
    dharve3: True
    lilahs: True

`hdcli.py lastpass {username}` 
Returns a dictionary displaying the timestamp (in UTC) of the user's last password change.
Example output:     
    {'lilahs': '2025-12-05T03:58:03Z'}

`hdcli.py lastpass {username}` 
Returns 
