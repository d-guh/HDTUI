from hdtools import client
import logging

def prompt_identity_choice(items):
    """Display a list and prompt for choice"""
    for i, item in enumerate(items, start=1):
        name = item.get("preferredName", [""]) or [""]
        first = item.get("firstName", [""]) or [""]
        last = item.get("lastName", [""]) or [""]
        uname = item.get("primaryUserName", [""]) or [""]

        display_name = name[0] if name[0] else first[0]
        print(f"{i}. {display_name} {last[0]} ({uname[0] or '<no username>'})")

    while True:
        choice = input("Select [number]: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
        print("Invalid Selection.")

def run():
    print("Welcome to the HDTools CLI Interface.")
    print("Type 'help' for commands. Type 'exit' to quit.")

    while True:
        try:
            line = input("> ").strip()
            if not line:
                continue

            if line.lower() in ("exit", "quit", "q"):
                print("Exiting CLI.")
                break

            if line.lower() == "help":
                print("\nAvailable Commands:")
                print("  search <username|full name>  - Search user")
                print("  help                         - Show this help")
                print("  exit                         - Quit the CLI\n")
                continue
            
            if " " in line:
                cmd, arg = line.split(" ", 1)
            else:
                cmd, arg = line, ""

            cmd = cmd.lower()

            if cmd == "search":
                if not arg.strip():
                    print("Usage: search <username|full name>")
                    continue

                results = client.search_user(arg)
                if not results:
                    print(f"No results for {arg}")
                    continue

                if len(results) == 1:
                    user = results[0]
                    print(f"\n Auto Selected: {user.get('firstName', [''])[0]} {user.get('lastName', [''])[0]}")
                else:
                    print(f"\nResults for {arg}:")
                    user = prompt_identity_choice(results)

                zid = user['zid']
                print(f"\nSelected identity for: {user.get('firstName', [''])[0]} {user.get('lastName', [''])[0]}")

                fullname = client.get_name_by_id(zid)
                if isinstance(fullname, list):
                    print(f"Full Name: {fullname[0]}")
                else:
                    print(f"Full Name: {fullname}")

                modules = client.get_modules()["nav"]
                print("\nAvailable Modules:")
                indexed_modules = []

                for idx, m in enumerate(modules, start=1):
                    mod = m["module"]
                    label = m["label"]
                    authed = client.check_module_auth(mod, zid)
                    if authed is None:
                        status = "SK"
                    else:
                        status = "OK" if authed else "NO"
                    print(f" {idx}. [{status}] {label} ({mod})")
                    indexed_modules.append((mod, label, status))

                while True:
                    print("\nType the number of the module you want to open (or press q to quit):")
                    mod_choice = input("Module #: ").strip().lower()
                    if mod_choice == "q":
                        break
                    if mod_choice == "":
                        print("Skipping selection, defaulting to identity.")
                        mod_choice = "1"
                    if mod_choice.isdigit():
                        idx = int(mod_choice) - 1
                        if 0 <= idx < len(indexed_modules):
                            if indexed_modules[idx][2] != "OK":
                                print("Module is not available.")
                                continue
                            selected_mod, label, status = indexed_modules[idx]
                            print(f"\nFetching module '{label}' ({selected_mod})...")
                            if selected_mod == "eventLogNew":
                                mod_json = client.get_vault_module(zid)
                            else:
                                mod_json = client.get_module(selected_mod, zid)
                            print(f"\n=== {label} Module Info ===")

                            if selected_mod == "eventLogNew":
                                print(client.format_vault_history(mod_json))
                            else:
                                print(client.format_module(mod_json))
                            print("-" * 40)
                    else:
                        print("Invalid selection. Please enter a valid number or press enter to skip.")
            else:
                print(f"Unknown command: {line}")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting CLI.")
            break
        except Exception as e:
            print(f"Error: {e}")
            # logging.exception("Caught the following exception:")
