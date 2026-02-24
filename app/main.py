import os
import sys
import subprocess
import shlex
import readline
from io import StringIO

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

def auto_complete(text, state):    
    execs = get_path_execs()

    all_cmds = set(builtin) | execs

    match = sorted(cmd for cmd in all_cmds if cmd.startswith(text))

    if state < len(match):
        return match[state] + " "
    
    return None

def get_path_execs():
    execs = set()
    path_env = os.environ.get("PATH", "")

    for dir in path_env.split(os.pathsep):
        if not os.path.isdir(dir):
            continue

        for file in os.listdir(dir):
            full_path = os.path.join(dir, file)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                execs.add(file)

    return execs

def run_pipe(cmd_input):
    left, right = cmd_input.split("|", 1)

    left_parts = shlex.split(left.strip())
    right_parts = shlex.split(right.strip())

    left_cmd = left_parts[0]
    right_cmd = right_parts[0]

    left_builtin = builtin.get(left_cmd)
    right_builtin = builtin.get(right_cmd)

    try:
        # builtin | external cmd
        if left_builtin and not right_builtin:
            old_stdout = sys.stdout
            buffer = StringIO()

            sys.stdout = buffer
            left_builtin(left_parts[1:])
            sys.stdout = old_stdout

            data = buffer.getvalue().encode()

            right_exec = find_execute(right_cmd)
            if not right_exec:
                print(f"{right_exec}: command not found")
                return
            
            subprocess.run([right_cmd] + right_parts[1:], executable=right_exec, input=data)

            return
        
        # external cmd | builtin
        if right_builtin and not left_builtin:

            left_exec = find_execute(left_cmd)
            
            if not left_exec:
                print(f"{left_exec}: command not found")
                return
            
            subprocess.run([left_cmd] + left_parts[1:], executable=right_exec, stdout=subprocess.DEVNULL)

            right_builtin(right_parts[1:])

            return
        
        # external | external
        left_exec = find_execute(left_cmd)
        right_exec = find_execute(right_cmd)

        if not left_exec:
            print(f"{left_parts[0]}: command not found")
            return
        
        if not right_exec:
            print(f"{right_parts[0]}: command not found")
            return
        
        p1 = subprocess.Popen([left_parts[0]] + left_parts[1:], executable=left_exec, stdout=subprocess.PIPE)
        p2 = subprocess.Popen([right_parts[0]] + right_parts[1:], executable=right_exec, stdin=p1.stdout)

        p1.stdout.close()

        p2.wait()
        p1.wait()

    except Exception as e:
        print("Pipeline error:", e)

builtin = {"echo": cmd_echo, "exit": cmd_exit, "type": cmd_type}

readline.set_completer(auto_complete)
readline.parse_and_bind("tab: complete")

def main():
    while True:
        cmd_input = input("$ ").strip()
        if not cmd_input:
            continue

        if "|" in cmd_input:
            run_pipe(cmd_input)
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