import argparse
import json
import shlex

from hdtools import config, client, cli, tui

# TODO: Add client update actions (button endpoints)
# TODO: Clean up CLI stuff (Grab useful bit of output)
# TODO: Clean up TUI stuff (Improve UX)
# TODO: Active User Command, Password Reset Command, Info/Note Command
# TODO: Maybe remove auth check if slowing too much? (CLI/TUI)
# TODO: Improve documentation, add type hinting for params and returns

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
    parser.add_argument('-i', '--input', help='Input file (ex. list of usernames)')

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-o', '--output', metavar='FILE', help='Write plaintext output to a file')
    output_group.add_argument('-oJ', '--output_json', metavar='FILE', help='Write JSON output to a file')
    output_group.add_argument('-oA', '--output_all', metavar='FILE', help='Write all output types to files')

    subparser = parser.add_subparsers(dest='command', help='Available Commands')

    # `cli` command
    cli_parser = subparser.add_parser('cli', help='Run interactive CLI interface')

    # `tui` command
    tui_parser = subparser.add_parser('tui', help='Run interactive TUI interface')

    # `search` command
    search_parser = subparser.add_parser('search', help='Search for one or more users')
    search_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to search')

    # `lastpass` command
    search_parser = subparser.add_parser('lastpass', help='Check the last password change time for one or more users')
    search_parser.add_argument('usernames', nargs='*', metavar='USERNAME', help='Username(s) to check')

    args = parser.parse_args()
    config.init_logging(args.debug)

    client.setup_session()

    if args.command == 'cli':
        cli.run()
    elif args.command == 'tui':
        tui.run()
    elif args.command == 'search':
        usernames = load_usernames(args)
        results = {user: client.search_user(user) for user in usernames}
        handle_output(results, args, formatter=None)
    elif args.command == 'lastpass':
        usernames = load_usernames(args)
        results = {}
        for user in usernames:
            try:
                results[user] = client.get_last_password_change(user)
            except Exception as e:
                results[user] = {"error": str(e)}
        handle_output(results, args, formatter=None)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
