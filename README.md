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
All of these commands can be run with any number/format of input for usernames, either via the input flag `-i {FILE}` or on the command line.

They can also all be run with different output modes. The default is `-pN` or `--print_normal` which uses custom formatters to make human readable output. Theres flags for writing to files `-oN` or `--output_normal` with more for JSON or other formats (see `-h`).

#### `hdcli.py abroad {username}`
Returns the users abroad status based on the classes they are taking.
```
dharve3: Local
lilahs: Abroad
```
#### `hdcli.py active {username}` 
Returns the users active status based on account health.
```
dharve3: Active
lilahs: Inactive
```
#### `hdcli.py department {username}`
Returns the user's department(s). Will display None if they are not an employee.
```
dharve3:Experiential Education;CCIT Customer Support Services
deshull:None
```
#### `hdcli.py lastpass {username}` 
Returns a dictionary displaying the timestamp (in UTC) of the user's last password change.
```
dharve3: 2022-12-16T04:54:24Z
lilahs: 2025-12-05T05:58:17Z
```
#### `hdcli.py lockout {username}`
Returns the users account status based on lockouts.
```
dharve3: Unlocked
lilahs: Unlocked
deshull: Locked
```
#### `hdcli.py -i FILE login`
Performs a login attempt with the given credentials. Note that you MUST use an input file here, with the format `username \t password` (tab separated) as proviing passwords on the commandline is not permitted.
```
dharve3: Failed
lilahs: Succeeded
```
#### `hdcli.py reset {username}`
Performs a password reset for the given users. Outputs the temporary password.
```
LEANNA: Password reset to '[REDACTED]'
```
#### `hdcli.py search {username}`
Returns basic information about the user, including: ZID, name, identity type, suffix, primary affiliation, affiliations, usernames, XID, CUID, employee ID, and VIP status.
```
test | firstName: Test | lastName: User | affiliations: affiliate | userNames: TEST | XID: C38125957
```
#### `hdcli.py supervisor {username}`
Returns the user's supervisor(s). Returns None if not an employee.
```
dharve3:Nunamaker,Troy D;Price,Brian A
lilahs:Nunamaker,Troy D
deshull:None
```