import argparse
import datetime
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
        data = json.load(f)
    # Old files hold plain names. New files hold {"name", "done"} objects.
    return [{"name": h, "done": []} if isinstance(h, str) else h for h in data]


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
        if saved["name"].lower() == name.lower():
            print(f"habit already exists: {saved['name']}", file=sys.stderr)
            return 1
    habits.append({"name": name, "done": []})
    save_habits(habits)
    print(f"added: {name}")
    return 0


def today():
    return os.environ.get("HABITS_TODAY") or datetime.date.today().isoformat()


def streak(done, day):
    days = set(done)
    current = datetime.date.fromisoformat(day)
    if current.isoformat() not in days:
        current -= datetime.timedelta(days=1)
    count = 0
    while current.isoformat() in days:
        count += 1
        current -= datetime.timedelta(days=1)
    return count


def cmd_list(args):
    day = today()
    for habit in load_habits():
        if args.streaks:
            print(f"{habit['name']}: {streak(habit['done'], day)}")
        else:
            print(habit["name"])
    return 0


def cmd_done(args):
    wanted = args.name.strip().lower()
    habits = load_habits()
    for habit in habits:
        if habit["name"].lower() == wanted:
            day = today()
            if day in habit["done"]:
                print(f"already done today: {habit['name']}")
                return 0
            habit["done"].append(day)
            save_habits(habits)
            print(f"done: {habit['name']}")
            return 0
    print(f"no such habit: {args.name}", file=sys.stderr)
    return 1


def build_parser():
    parser = argparse.ArgumentParser(prog="habits", description="Habit tracker.")
    subparsers = parser.add_subparsers(dest="command", metavar="command", required=True)
    add = subparsers.add_parser("add", help="add a habit")
    add.add_argument("name")
    add.set_defaults(func=cmd_add)
    lst = subparsers.add_parser("list", help="list all habits")
    lst.add_argument("--streaks", action="store_true", help="show current streaks")
    lst.set_defaults(func=cmd_list)
    done = subparsers.add_parser("done", help="mark a habit done for today")
    done.add_argument("name")
    done.set_defaults(func=cmd_done)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)
