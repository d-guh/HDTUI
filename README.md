# HDTUI
A commandline/TUI wrapper for accessing HDTools. Has script integration, designed to be an all in one tool for HDTools automation and usage. Can also prove useful while developing new scripts.

Written by Dylan Harvey in Summer 2025

## Setup
Install python (apt/download etc.) Note on debian based distros you need: `python3` `python3-venv` `python3-pip`\
`python -m venv .venv`\
`pip install -r requirements.txt`

## Usage
`hdtui.py -h` for addtional help/usage information. Commands also have additonal help menus.\
**This tool has a few modes:**
### Command Mode
`hdtui.py {COMMAND}`
You can use a variety of commands directly from the commandline to get text and json output. Useful for batch jobs (input file) or automations.

### CLI Mode
`hdtui.py cli`
Creates an interactive command line to access HDTools in. Similar but simplistic compared to browser functionality.

### TUI Mode (WIP)
`hdtui.py tui`
Creates an interactive TUI to access HDTools in. Mirrors browser functionality as close as possible.

### Example Commands - All can be run with multiple username arguments.
`hdtui.py search {username}`
Returns basic information about the user, including: ZID, first, middle, and last 
name, identity type, suffix, primary affiliation, affiliations, usernames, XID, CUID, employee ID, 
and VIP status.

`hdtui.py reset {username}`
Resets the user's password and returns the new password. Adds a description noting that the password was reset by IT Security at the current date and time. Example output:
    {'lilahs': {'SuccessMessage': 'Password reset to <br><br><b>hefty oasis clockXXXXX (Last 5 of SSN)</b><br><br>If servers are busy, this could take several minutes to complete.<br>Requesting another reset will not speed up this process.', 'description': ['12/04/2025 22:56 - Password reset by CCIT Security']}}

`hdtui.py department {username}`
Returns the user's department(s). Example output:
    dharve3:Experiential Education;CCIT Customer Support Services

`hdtui.py supervisor {username}`
Returns the user's supervisor(s). Example output:
    dharve3:Nunamaker,Troy D;Price,Brian A

`hdtui.py abroad {username}`
Returns a dictionary storing the user's abroad status, with true indicating the 
user is abroad and false indicating the user is local. Example output:
    {'dharve3': False, 'lilahs': False}

`hdtui.py active {username}` 
Returns a list displaying whether the user's account is active or not, with true indicating an
active account and false indicating an inactive account. Example output:
    dharve3: True
    lilahs: True

`hdtui.py lastpass {username}` 
Returns a dictionary displaying the timestamp (in UTC) of the user's last password change.
Example output:     
    {'lilahs': '2025-12-05T03:58:03Z'}

`hdtui.py lastpass {username}` 
Returns 



