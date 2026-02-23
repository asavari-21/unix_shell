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

        parts = shlex.split(cmd_input)

        out_file = None
        err_file = None
        app_out_file = None
        app_err_file = None

        while True:
            if ">>" in parts:
                i = parts.index(">>")
                app_out_file = parts[i+1]
                parts = parts[:i]

            elif "1>>" in parts:
                i = parts.index("1>>")
                app_out_file = parts[i+1]
                parts = parts[:i]

            elif "2>>" in parts:
                i = parts.index("2>>")
                app_err_file = parts[i+1]
                parts = parts[:i]
            
            elif ">" in parts:
                i = parts.index(">")
                out_file = parts[i+1]
                parts = parts[:i]

            elif "1>" in parts:
                i = parts.index("1>")
                out_file = parts[i+1]
                parts = parts[:i]

            elif "2>" in parts:
                i = parts.index("2>")
                err_file = parts[i+1]
                parts = parts[:i]
            
            else:
                break

        cmd = parts[0]
        args = parts[1:]

        func = builtin.get(cmd)

        if func:
            old_out = sys.stdout
            old_err = sys.stderr

            try:
                if app_out_file:
                    sys.stdout = open(app_out_file, "a")
                elif out_file:
                    sys.stdout = open(out_file, "w")

                if app_err_file:
                    sys.stderr = open(app_err_file, "a")
                elif err_file:
                    sys.stderr = open(err_file, "w")                

                func(args)

            finally:
                if sys.stdout is not old_out:
                    sys.stdout.close()
                if sys.stderr is not old_err:
                    sys.stderr.close()
                
                sys.stdout = old_out
                sys.stderr = old_err

        else:
            full_path = find_execute(cmd)

            if full_path:
                try:
                    out_tar = None
                    err_tar = None

                    if app_out_file:
                        out_tar = open(app_out_file, "a")
                    elif out_file:
                        out_tar = open(out_file, "w")
                    
                    if app_err_file:
                        err_tar = open(app_err_file, "a")
                    if err_file:
                        err_tar = open(err_file, "w")                   
                    
                    subprocess.run([cmd] + args, executable=full_path, stdout=out_tar, stderr=err_tar)

                    if out_tar: 
                        out_tar.close()
                    if err_tar:
                        err_tar.close()

                except Exception as e:
                    print(f"Error executing {cmd}: {e}")
            else:
                print(f"{cmd}: command not found")

if __name__ == "__main__":
    main()