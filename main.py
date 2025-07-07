import argparse
from hdtools import config, client, tui

# TODO: Logging library for debug
# TODO: Fix/Add more commands (identity, etc.; should output specific info if cmdline arg)
# TODO: Format help output (section for commands etc)
# TODO: Fix client
# TODO: Clean up CLI stuff (Grab useful bit of output)
# TODO: Clean up TUI stuff (Improve UX)

def main():
    config.load_dotenv()

    parser = argparse.ArgumentParser(description="HDTools CLI Wrapper")
    parser.add_argument('-m', '--mode', choices=['cli', 'tui'], default='cli', help="Run Mode") # Default CLI for scripts, if using a command flag should exit upon gathering data, if no command flag used, open interactive mode in TUI or CLI
    parser.add_argument('-s', '--search', help="Search user (CLI Only)")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output")
    args = parser.parse_args()

    if args.debug:
        config.DEBUG = True
    if args.mode == 'tui':
        tui.run()
    else:
        if args.search:
            result = client.search_user(args.search)
            print(result)
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
