import os
import sys
import subprocess
import shlex

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
    
    full_path = find_execute(cmd)
    if full_path:
        print(f"{cmd} is {full_path}")
    else:       
        print(f"{cmd}: not found")

def find_execute(cmd):
    path_env = os.environ.get("PATH", "")
    paths = path_env.split(os.pathsep)

    for dir in paths:
        full_path = os.path.join(dir, cmd)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
        
    return None


builtin = {"echo": cmd_echo, "exit": cmd_exit, "type": cmd_type}

def main():
    while True:
        cmd_input = input("$ ").strip()
        if not cmd_input:
            continue

        cmd = cmd_input.split()[0]
        args = shlex.split(cmd_input)[1:]

        func = builtin.get(cmd)
        if func:
            func(args)
        else:
            full_path = find_execute(cmd)
            if full_path:
                try:
                    subprocess.run([cmd] + args, executable=full_path)
                except Exception as e:
                    print(f"Error executing {cmd}: {e}")
            else:
                print(f"{cmd}: command not found")

if __name__ == "__main__":
    main()