#!/usr/bin/env python
import argparse
import json
import shlex

from hdtools import config, client, cli, tui

# TODO: Consider hardcoding all the endpoints tbh
# TODO: Add simple endpoint for getting user ID etc.
# TODO: Handle people with multiple usernames better (check active?)
# TODO: Add more commands: login, abroad, reset password, department
# TODO: Add client update actions (button endpoints)
# TODO: Clean up CLI stuff (Grab useful bit of output)
# TODO: Clean up TUI stuff (Improve UX)
# TODO: Maybe remove auth check if slowing too much? (CLI/TUI)
# TODO: Improve documentation, add type hinting for params and returns

def handle_cli(args):
    cli.run()

def handle_tui(args):
    tui.run()

def handle_abroad(args):
    usernames = load_usernames(args)
    results = {}
    for user in usernames:
        try:
            results[user] = client.get_abroad_status(user)
        except Exception as e:
            results[user] = {"error": str(e)}
    if args.filter != "all":
        target = args.filter.lower()
        results = {user: status for user, status in results.items()
                    if isinstance(status, bool) and ((status and target == "abroad") or (not status and target == "local"))}
    handle_output(results, args, formatter=None)

def handle_active(args):
    usernames = load_usernames(args)
    results = {}
    for user in usernames:
        try:
            results[user] = client.get_user_status(user)
        except Exception as e:
            results[user] = {"error": str(e)}
    if args.filter != "all":
        target = args.filter.lower()
        results = {user: status for user, status in results.items()
                    if isinstance(status, bool) and ((status and target == "active") or (not status and target == "inactive"))}
    handle_output(results, args, formatter=None)

def handle_department(args):
    pass

def handle_lastpass(args):
    usernames = load_usernames(args)
    results = {}
    for user in usernames:
        try:
            results[user] = client.get_last_password_change(user)
        except Exception as e:
            results[user] = {"error": str(e)}
    handle_output(results, args, formatter=None)

def handle_lockout(args):
    usernames = load_usernames(args)
    results = {}
    for user in usernames:
        try:
            data = client.get_user_data(user)
            vaultzid, username = client.extract_id_and_username(data)
            module = client.get_module('usernamesHDStudent', vaultzid)
            results[user] = (module.get('activeDirectoryLockout') == 'true')
        except Exception as e:
            results[user] = {"error": str(e)}
    if args.filter != "all":
        target = args.filter.lower()
        results = {user: status for user, status in results.items()
                    if isinstance(status, bool) and ((status and target == "locked") or (not status and target == "unlocked"))}
    handle_output(results, args, formatter=None)

def handle_login(args):
    pass

def handle_reset(args):
    pass

def handle_search(args):
    usernames = load_usernames(args)
    results = {user: client.search_user(user) for user in usernames}
    handle_output(results, args, formatter=None)

def load_usernames(args):
    """Loads usernames from input file and/or CLI, normalizes with parse_username"""
    usernames = list(args.usernames) if args.usernames else []

    if args.input:
        with open(args.input) as f:
            content = f.read()
            # Split on spaces, newlines, and respecting quotes
            file_usernames = shlex.split(content)
            usernames.extend(file_usernames)

    return [client.parse_username(user) for user in usernames if user.strip()]

def handle_output(data, args, formatter=None):
    """Generic output handler for plain/JSON/all output modes."""
    if args.output_all:
        with open(f"{args.output_all}.txt", "w") as f_txt, open(f"{args.output_all}.json", "w") as f_json:
            f_txt.write(formatter(data) if formatter else str(data))
            json.dump(data, f_json, indent=2)
    elif args.output:
        with open(args.output, "w") as f_txt:
            f_txt.write(formatter(data) if formatter else str(data))
    elif args.output_json:
        with open(args.output_json, "w") as f_json:
            json.dump(data, f_json, indent=2)
    else:
        if formatter:
            print(formatter(data))
        else:
            # print(json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data))
            print(str(data))

def main():
    """Entry point, handles command line arguments and flow"""
    config.load_dotenv()

    parser = argparse.ArgumentParser(description="HDTools Wrapper", add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="Show this help message and exit")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output")
    parser.add_argument('-i', '--input', metavar='FILE', help='Input file (ex. list of usernames)')

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-o', '--output', metavar='FILE', help='Write plaintext output to a file')
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
    active_parser.add_argument('-f', '--filter', choices=['all', 'active', 'inactive'], default='all', help='Filter output by user activity status')
    active_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    # `department` command
    department_parser = command_subparser.add_parser('department', help='Check the department for one or more users')
    department_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    # `lastpass` command
    search_parser = command_subparser.add_parser('lastpass', help='Check the last password change time for one or more users')
    search_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

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
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
