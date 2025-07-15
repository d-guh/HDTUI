import argparse
from hdtools import config, client, cli, tui

# TODO: Add client update actions (button endpoints)
# TODO: Clean up CLI stuff (Grab useful bit of output)
# TODO: Clean up TUI stuff (Improve UX)
# TODO: Active User Command, Password Reset Command, Info/Note Command
# TODO: Maybe remove auth check if slowing too much?

def main():
    config.load_dotenv()


    parser = argparse.ArgumentParser(description="HDTools Wrapper", add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="Show this help message and exit")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output")

    subparser = parser.add_subparsers(dest='command', help='Available Commands')

    # `search` command
    search_parser = subparser.add_parser('search', help='Search for one or more users')
    search_parser.add_argument('usernames', nargs='+', metavar='USERNAME', help='Username(s) to search')
    
    # `cli` command
    cli_parser = subparser.add_parser('cli', help='Run interactive CLI interface')

    # `tui` command
    tui_parser = subparser.add_parser('tui', help='Run interactive TUI interface')

    args = parser.parse_args()
    config.init_logging(args.debug)

    if args.command == 'cli':
        cli.run()
    elif args.command == 'tui':
        tui.run()
    elif args.command == 'search':
        for username in args.usernames:
            print(client.search_user(username))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
