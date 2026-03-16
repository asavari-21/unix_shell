import os
import sys
import subprocess
import shlex
import readline

readline.set_completer_delims(" \t\n")
readline.parse_and_bind("tab: complete")

from io import StringIO

#print(f"DEBUG: sys.path is {sys.path}", file=sys.stderr)

def cmd_exit(args: any):
    histfile = os.environ.get("HISTFILE")

    if histfile:
        try:
            with open(histfile, "w") as f:
                for cmd in history:
                    f.write(cmd + "\n")
        except FileNotFoundError:
            pass        
    sys.exit()

def cmd_echo(args: str):
    print(" ".join(args))

def cmd_pwd(args):
    print(os.getcwd())

def cmd_cd(args):

    if not args:
        path = os.path.expanduser("~")
    else:
        path = args[0]

        if path == "~":
            path = os.path.expanduser("~")
        else:
            path = os.path.expanduser(path)
        
    try:
        os.chdir(path)
    except FileNotFoundError:
        print(f"cd: {path}: No such file or directory")
    except NotADirectoryError:
        print(f"cd: {path}: Not a directory")

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

# def auto_complete(text, state):
#     execs = get_path_execs()
#     all_cmds = set(builtin) | execs
#     match = sorted(cmd for cmd in all_cmds if cmd.startswith(text))
#     if state < len(match):
#         return match[state] + " " 
#     return None

def auto_complete(text, state):

    buffer = readline.get_line_buffer()
    begidx = readline.get_begidx()
    endidx = readline.get_endidx()
    #tokens = buffer[:readline.get_begidx()].split()

    #if len(tokens) == 0:
    if begidx == 0:
        cmds = set(builtin.keys()) | get_path_execs()
        matches = sorted(cmd for cmd in cmds if cmd.startswith(text))

        if state < len(matches):
            return matches[state] + " " 
        return None
    
    if "/" in text:
        dirname, part = os.path.split(text)
        search_dir = os.path.expanduser(dirname) if dirname else "."
    else:
        dirname = ""
        part = text
        search_dir = "."

    try:
        entries = os.listdir(search_dir)
    except Exception:
        return None
    
    matches = sorted(e for e in entries if e.startswith(part))

    if state >= len(matches):
        return None
    
    match = matches[state]

    full_match_path = os.path.join(search_dir, match)

    if dirname:
        completion = os.path.join(dirname, match)
    else:
        completion = match
    
    if os.path.isdir(full_match_path):
        return completion + "/"
    else:
        return completion + " "

readline.set_completer(auto_complete)

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
    cmds = [shlex.split(cmd.strip()) for cmd in cmd_input.split("|")]

    processes = []
    prev_stdout = None


    try:
        for i, parts in enumerate(cmds):
            cmd_name = parts[0]
            args = parts[1:]

            func = builtin.get(cmd_name)

            if func:

                if i != len(cmds) - 1:
                    old_stdout = sys.stdout
                    buffer = StringIO()

                    sys.stdout = buffer
                    func(args)
                    sys.stdout = old_stdout

                    prev_stdout = buffer.getvalue().encode()

                else:
                    func(args)

                continue

            exec_path = find_execute(cmd_name)

            if not exec_path:
                print(f"{cmd_name}: command not found")
                return
            
            if i == 0:

                p = subprocess.Popen([cmd_name] + args, executable=exec_path, stdout=subprocess.PIPE)

                prev_stdout = p.stdout
                processes.append(p)

            elif i < len(cmds) - 1:

                if isinstance(prev_stdout, bytes):

                    p = subprocess.Popen([cmd_name] + args, executable=exec_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

                    p.stdin.write(prev_stdout)
                    p.stdin.close()

                else:

                    p = subprocess.Popen([cmd_name] + args, executable=exec_path, stdin=prev_stdout, stdout=subprocess.PIPE)

                    prev_stdout.close()

                prev_stdout = p.stdout
                processes.append(p)

            else:

                if isinstance(prev_stdout, bytes):

                    subprocess.run([cmd_name] + args, executable=exec_path, input=prev_stdout)

                else:
                     
                    p = subprocess.Popen([cmd_name] + args, executable=exec_path, stdin=prev_stdout)

                    prev_stdout.close()
                    p.wait()
                    processes.append(p)

        for p in processes:
            p.wait()

    except Exception as e:
        print("Pipeline error:", e)

history = []
last_written = 0
histfile = os.environ.get("HISTFILE")

if histfile:
    try:
        with open(histfile) as f:
            for line in f:
                cmd = line.strip()
                if cmd:
                    history.append(cmd)

        last_written = len(history)

    except FileNotFoundError:
        pass

def cmd_hist(args):

    if args and args[0] == "-r":
        if len(args) < 2:
            return
        
        path = args[1]

        try:
            with open(path) as f:
                for line in f:
                    cmd = line.strip()
                    if cmd:
                        history.append(cmd)
                
        except FileNotFoundError:
            print(f"history: {path}: no such file")        
        return
    
    if args and args[0] == "-w":
        if len(args) < 2:
            return
        
        path = args[1]

        with open(path, "w") as f:
            for cmd in history:
                f.write(cmd + "\n")       
        return
    
    global last_written
    
    if args and args[0] == "-a":
        if len(args) < 2:
            return
        
        path = args[1]

        with open(path, "a") as f:
            for cmd in history[last_written:]:
                f.write(cmd + "\n")
        
        last_written = len(history)
        return
        

    if args:
        try:
            n = int(args[0])
        except ValueError:
            print(f"history: invalid argument")
            return
    else:
        n = len(history)

    start = max(0, len(history) - n)

    for i in range(start, len(history)):
        print(f"{    i+1:5} {history[i]}") 

builtin = {"echo": cmd_echo, "exit": cmd_exit, "type": cmd_type, "history": cmd_hist, "pwd": cmd_pwd, "cd": cmd_cd} 

def main():
    while True:
        cmd_input = input("$ ")

        if not cmd_input.strip():
            continue
            
        history.append(cmd_input)

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