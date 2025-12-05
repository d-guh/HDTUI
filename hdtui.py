#!/usr/bin/env python
import argparse
import json
import logging

from hdtools import config, client, cli, tui

# TODO: Make getModule have a list of default args to make it easier to find endpoints
# TODO: Add simple endpoint for getting user ID from username search
# TODO: Handle people with multiple usernames better (check active/primary?)
# TODO: Add generic parser for module data?
# TODO: Custom formatters/output display, CSV, simple plaintext, XML?
# TODO: Add client update actions (button endpoints)
# TODO: Clean up CLI stuff (Grab useful bit of output)
# TODO: Clean up TUI stuff (Improve UX)
# TODO: Maybe remove auth check if slowing too much (only returns available modules anyways) (CLI/TUI)
# TODO: Improve documentation, add type hinting for params and returns

def handle_cli(args):
    cli.run()

def handle_tui(args):
    tui.run()

def handle_abroad(args):
    """Used to determine if a user is currently studying/working abroad. Returns a dictionary of 
    users with a boolean value indicating if they are abroad (True) or local (False). A filter
    can be applied to only show abroad/local users."""
    credentials = load_credentials(args)
    results = {}
    for username, password in credentials:
        try:
            results[username] = client.get_abroad_status(username)
        except Exception as e:
            results[username] = {"error": str(e)}
    if args.filter != "all":
        target = args.filter.lower()
        results = {username: status for username, status in results.items()
                    if isinstance(status, bool) and ((status and target == "abroad") or (not status and target == "local"))}
    handle_output(results, args, formatter=None)

def handle_active(args):
    """Used to determine if a user is currently active. Returns a dictionary of 
    users with a boolean value indicating if they are active (True) or inactive(False). A filter
    can be applied to only show inactive/active users."""
    credentials = load_credentials(args)
    results = {}
    for username, password in credentials:
        try:
            user_status = client.get_user_status(username)
            lockout_status = False
            logging.debug(f"STATUS: lockout_status: {username}: {lockout_status}")
            if args.locked:
                data = client.get_user_data(username)
                vaultzid, username = client.extract_id_and_username(data)
                lockout_status = client.get_module('usernamesHDStudent', vaultzid)['items'][0]['data'].get('activeDirectoryLockout', '') # this is a mess, sorry, also sometimes its false, sometimes empty string bruh
                if lockout_status == '':
                    lockout_status = False
                results[username] = lockout_status
            if not user_status or lockout_status:
                results[username] = False
            else:
                results[username] = user_status
        except Exception as e:
            if str(e) == '0':
                results[username] = "Not Found"
            else:
                results[username] = {"error": str(e)}
    if args.filter != "all":
        target = args.filter.lower()
        results = {username: status for username, status in results.items()
                    if isinstance(status, bool) and ((status and target == "active") or (not status and target == "inactive"))}
    handle_output(results, args, formatter=format_active)

def handle_department(args):
    """Used to get the department(s) for one or more users. Returns a dictionary of users
    with a list of their associated department names."""
    credentials = load_credentials(args)
    results = {}
    for username, password in credentials:
        try:
            data = client.get_user_data(username)
            vaultzid, username = client.extract_id_and_username(data)

            module = client.get_module('employeeRecords', vaultzid)
            items = module.get('items', [])
            results[username] = []

            for item in items:
                data = item.get('data', {})
                if data.get('objectId') == 'employeeRecords' and data.get('status') == 'A':
                    results[username].append(data.get('departmentName'))
        except Exception as e:
            results[username] = {"error": str(e)}
    handle_output(results, args, formatter=format_department)

def handle_lastpass(args):
    """Used to get the last password change time for one or more users. Returns a dictionary of users
    with their last password change timestamp."""
    credentials = load_credentials(args)
    results = {}
    for username, password in credentials:
        try:
            results[username] = client.get_last_password_change(username)
        except Exception as e:
            results[username] = {"error": str(e)}
    handle_output(results, args, formatter=None)

def handle_lockout(args):
    """Used to determine if a user currently has an AD lockout. Returns a dictionary of
    users with a boolean value indicating if they are locked out (True) or not (False). A filter
    can be applied to only show locked/unlocked users."""
    credentials = load_credentials(args)
    results = {}
    for username, password in credentials:
        try:
            data = client.get_user_data(username)
            vaultzid, username = client.extract_id_and_username(data)
            lockout_status = client.get_module('usernamesHDStudent', vaultzid)['items'][0]['data'].get('activeDirectoryLockout', '') # this is a mess, sorry, also sometimes its false, sometimes empty string bruh
            if lockout_status == '':
                lockout_status = False
            results[username] = lockout_status
        except Exception as e:
            results[username] = {"error": str(e)}
    if args.filter != "all":
        target = args.filter.lower()
        results = {username: status for username, status in results.items()
                    if isinstance(status, bool) and ((status and target == "locked") or (not status and target == "unlocked"))}
    handle_output(results, args, formatter=None)

def handle_login(args):
    """Attempts to login to one or more users. Returns a dictionary of users
    with the result of the login attempt."""
    credentials = load_credentials(args)
    results = {}
    for username, password in credentials:
        try:
            results[username] = client.check_login(username, password)
        except Exception as e:
            results[username] = {"error": str(e)}
    handle_output(results, args, formatter=None)

def handle_reset(args):
    """Resets the password for one or more users. Returns a dictionary of users
    with the result of the password reset attempt."""
    credentials = load_credentials(args)
    results = {}
    for username, password in credentials:
        try:
            data = client.get_user_data(username)
            vaultzid, username = client.extract_id_and_username(data)
            results[username] = {
                "SuccessMessage": client.reset_password(username, vaultzid).get("SuccessMessage"),
                "description": client.set_user_description(username, vaultzid).get("description")
            }
        except Exception as e:
            results[username] = {"error": str(e)}
    handle_output(results, args, formatter=None)

def handle_search(args):
    """Searches for one or more users. Returns a dictionary of users
    with the result of the search."""
    credentials = load_credentials(args)
    results = {username: client.search_user(username) for username, password in credentials}
    handle_output(results, args, formatter=format_search)

def handle_supervisor(args):
    """Used to get the supervisor(s) for one or more users. Returns a dictionary of users
    with a list of their associated supervisor names."""
    credentials = load_credentials(args)
    results = {}
    for username, password in credentials:
        try:
            data = client.get_user_data(username)
            vaultzid, username = client.extract_id_and_username(data)

            module = client.get_module('employeeRecords', vaultzid)
            items = module.get('items', [])
            results[username] = []

            for item in items:
                data = item.get('data', {})
                if data.get('objectId') == 'employeeRecords' and data.get('status') == 'A':
                    results[username].append(data.get('supervisorName'))      
        except Exception as e:
            results[username] = {"error": str(e)}
    handle_output(results, args, formatter=format_supervisor)

def extract_cred(x):
    y = x.split('\t')
    if len(y) == 1:
        return (y[0], None)
    elif len(y) == 2:
        return (y[0], y[1])
    else:
        return ('', None)

def load_credentials(args):
    """Loads credentials from input file and/or CLI, normalizes with parse_username"""
    credentials = list(map(lambda x: (x, None), args.usernames)) if args.usernames else [("", "")]

    if args.input:
        with open(args.input) as f:
            content = f.read()
            # Split on spaces, newlines, and respecting quotes
            file_credentials = list(map(extract_cred, content.split('\n')))
            credentials.extend(file_credentials)

    return [(client.parse_username(username), password) for username, password in credentials if username.strip()]

def handle_output(data, args, formatter=None):
    """Generic output handler for plain/JSON/all output modes."""
    if args.output_all:
        with open(f"{args.output_all}.txt", "w") as f_txt, open(f"{args.output_all}.json", "w") as f_json:
            f_txt.write(formatter(data) if formatter else str(data))
            json.dump(data, f_json, indent=2)
    elif args.output_normal:
        with open(args.output_normal, "w") as f_txt:
            f_txt.write(formatter(data) if formatter else str(data))
    elif args.output_json:
        with open(args.output_json, "w") as f_json:
            json.dump(data, f_json, indent=2)
    else:
        if formatter:
            print(formatter(data))
        else:
            print(str(data))

def format_department(data: dict) -> str:
    """Format department data into plain text output."""
    lines = []
    for name, departments in data.items():
        dept_str = ";".join(departments) if departments else "None"
        lines.append(f"{name}:{dept_str}")
    return "\n".join(lines)

def format_supervisor(data: dict) -> str:
    """Format supervisor data into plain text output."""
    lines = []
    for name, supervisors in data.items():
        sup_str = ";".join(supervisors) if supervisors else "None"
        lines.append(f"{name}:{sup_str}")
    return "\n".join(lines)

def format_active(data: dict) -> str:
    """Format active user data into plain text output."""
    lines = []
    for username, status in data.items():
        lines.append(f"{username}: {status}")
    return "\n".join(lines)

def format_search(data: dict) -> str:
    """Format search data into plain text output."""
    lines = []
    for username, results in data.items():
        for result in results:
            entry = [username]
            for key in ['firstName', 'lastName', 'affiliations', 'userNames', 'XID', 
                        'CUID', 'employeeId']:
                if key in result:
                    entry.append(f"{key}: {result[key]}")
        lines.append(" | ".join(entry)) 
    return "\n".join(lines)

def main():
    """Entry point, handles command line arguments and flow"""
    config.load_dotenv()

    parser = argparse.ArgumentParser(description="HDTools Wrapper", add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="Show this help message and exit")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output")
    parser.add_argument('-i', '--input', metavar='FILE', help='Input file (ex. list of credentials)')

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-oN', '--output_normal', metavar='FILE', help='Write plaintext output to a file')
    output_group.add_argument('-oJ', '--output_json', metavar='FILE', help='Write JSON output to a file')
    output_group.add_argument('-oA', '--output_all', metavar='FILE', help='Write all output types to files')

    command_subparser = parser.add_subparsers(dest='command', help='Available Commands')

    # `cli` command
    cli_parser = command_subparser.add_parser('cli', help='Run interactive CLI interface')

    # `tui` command
    tui_parser = command_subparser.add_parser('tui', help='Run interactive TUI interface')

    # `abroad` command
    abroad_parser = command_subparser.add_parser('abroad', help='Check if an account is currently studying abroad for one or more users')
    abroad_parser.add_argument('-f', '--filter', choices=['all', 'abroad', 'local'], default='all', help='Filter output by user abroad status')
    abroad_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    # `active` command
    active_parser = command_subparser.add_parser('active', help='Check if an account is active for one or more users')
    active_parser.add_argument('-l', '--locked', action='store_true', help='Treats users with AD lockouts as inactive')
    active_parser.add_argument('-f', '--filter', choices=['all', 'active', 'inactive'], default='all', help='Filter output by user activity status')
    active_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    # `department` command
    department_parser = command_subparser.add_parser('department', help='Check the department for one or more users')
    department_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    # `lastpass` command
    lastpass_parser = command_subparser.add_parser('lastpass', help='Check the last password change time for one or more users')
    lastpass_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    # `lockout` command
    lockout_parser = command_subparser.add_parser('lockout', help='Check if accounts currently have AD lockouts')
    lockout_parser.add_argument('-f', '--filter', choices=['all', 'locked', 'unlocked'], default='all', help='Filter output by user lockout status')
    lockout_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    # `login` command
    login_parser = command_subparser.add_parser('login', help='Attempt to login to one or more users')
    login_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to attempt')

    # `reset` command
    reset_parser = command_subparser.add_parser('reset', help='Reset a password for one or more users')
    reset_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to reset')

    # `search` command
    search_parser = command_subparser.add_parser('search', help='Search for one or more users')
    search_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to search')

    # `supervisor` command
    supervisor_parser = command_subparser.add_parser('supervisor', help='Get the supervisor(s) for one or more users')
    supervisor_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    args = parser.parse_args()
    config.init_logging(args.debug)
    client.setup_session()

    dispatch = {
        'cli': handle_cli,
        'tui': handle_tui,
        'abroad': handle_abroad,
        'active': handle_active,
        'department': handle_department,
        'lastpass': handle_lastpass,
        'lockout': handle_lockout,
        'login': handle_login,
        'reset': handle_reset,
        'search': handle_search,
        'supervisor': handle_supervisor
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()