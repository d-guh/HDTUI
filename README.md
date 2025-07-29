# HDTUI
A commandline/TUI wrapper for accessing HDTools. Has script integration, designed to be an all in one tool for HDTools automation and usage. Can also prove useful while developing new scripts.

Written by Dylan Harvey in Summer 2025

## Usage
`main.py -h` for addtional help/usage information. Commands also have additonal help menus.
This tool has a few modes:
### Command Mode
`main.py {COMMAND}`
You can use a variety of commands directly from the commandline to get text and json output. Useful for batch jobs (input file) or automations.

### CLI Mode
`main.py cli`
Creates an interative command line to access HDTools in. Similar to browser functionality.

### TUI Mode (WIP)
`main.py tui`
Creates an interactive TUI to access HDTools in. Supposed to mirror browser functionality as closely as possible.
