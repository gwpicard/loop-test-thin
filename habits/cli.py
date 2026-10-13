import argparse
import json
import os
import sys


def data_path():
    return os.environ.get("HABITS_FILE", "habits.json")


def load_habits():
    path = data_path()
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def save_habits(habits):
    with open(data_path(), "w") as f:
        json.dump(habits, f)


def cmd_add(args):
    name = args.name.strip()
    if not name:
        print("habit name is empty", file=sys.stderr)
        return 1
    habits = load_habits()
    for saved in habits:
        if saved.lower() == name.lower():
            print(f"habit already exists: {saved}", file=sys.stderr)
            return 1
    habits.append(name)
    save_habits(habits)
    print(f"added: {name}")
    return 0


def cmd_list(args):
    for name in load_habits():
        print(name)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="habits", description="Habit tracker.")
    subparsers = parser.add_subparsers(dest="command", metavar="command", required=True)
    add = subparsers.add_parser("add", help="add a habit")
    add.add_argument("name")
    add.set_defaults(func=cmd_add)
    lst = subparsers.add_parser("list", help="list all habits")
    lst.set_defaults(func=cmd_list)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)
