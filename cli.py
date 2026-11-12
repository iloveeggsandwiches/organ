import organ_main
import json
on = True

def load_formats(category):
    with open("organ/formats.json", "r") as k:
        read = json.load(k)
        final = list(read.get(category))
        return final

def load_copies(category, path="organ/db.json"):
    with open(path, "r") as f:
        data = json.load(f)

    formats = data.get(category, {})
    copies = []

    for fmt, tracks in formats.items():
        names = [track[0] for track in tracks]
        copies.append(f"{fmt}: {', '.join(names) or '(none)'}")
    return copies

while on:
    command = input("organcli>")

    if command == "music":
        print("Add Remove or list all formats/items: list, add, rem, list-items")
        subcommand = input("command:")
        if subcommand == "add":
            param = input("Name: ")
            param2 = input("Cover path (leave empty for no path): ")
            param3 = input("Format: ")
            organ_main.add_item(param,"music",param3,param2)
        if subcommand == "list":
            print("\n")
            for i in range(len(load_formats("music"))):
                print(f"{load_formats("music")[i]}")
            print("\n")
        if subcommand == "list-items":
            print("\n")
            for i in range(len(load_copies("music"))):
                print(load_copies("music")[i])
            print("\n")
        if subcommand == "rem":
            param = input("Name: ")
            param2 = input("Format: ")
            organ_main.delete_item(param,"music",param2)
    elif command == "exit":
        on = False
    if command == "movies":
        print("Add Remove or list all formats/items: list, add, rem, list-items")
        subcommand = input("command:")
        if subcommand == "add":
            param = input("Name: ")
            param2 = input("Cover path (leave empty for no path): ")
            param3 = input("Format: ")
            organ_main.add_item(param,"movies",param3,param2)
        if subcommand == "list":
            print("\n")
            for i in range(len(load_formats("movies"))):
                print(f"{load_formats("movies")[i]}")
            print("\n")
        if subcommand == "list-items":
            print("\n")
            for i in range(len(load_copies("movies"))):
                print(load_copies("movies")[i])
            print("\n")
        if subcommand == "rem":
            param = input("Name: ")
            param2 = input("Format: ")
            organ_main.delete_item(param,"movies",param2)