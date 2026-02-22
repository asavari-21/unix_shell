import os
import sys

def cmd_exit(args: any):
    sys.exit()

def cmd_echo(args: str):
    print(" ".join(args))

def cmd_type(args: str):
    if not args:
        print("type: missing argument")
        return
    
    cmd = args[0]
    if cmd in builtin:
        print(f"{cmd} is a shell builtin")
        return
    
    path_env = os.environ.get("PATH", "")
    paths = path_env.split(os.pathsep)

    for dir in paths:
        full_path = os.path.join(dir, cmd)

        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            print(f"{cmd} is {full_path}")
            return
        
    print(f"{cmd}: not found")

builtin = {"echo": cmd_echo, "exit": cmd_exit, "type": cmd_type}

def main():
    while True:
        cmd_input = input("$ ").strip()
        if not cmd_input:
            continue

        cmd = cmd_input.split()[0]
        args = cmd_input.split()[1:]

        func = builtin.get(cmd)
        if func:
            func(args)
        else:
            print(f"{cmd}: command not found")

if __name__ == "__main__":
    main()