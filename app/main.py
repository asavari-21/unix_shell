import sys


def main():
    # sys.stdout.write("$ ")
    # pass
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == "exit":
            sys.exit()
        elif command.split()[0] == "echo":
            for i in range (1, len(command.split())):
                print(command.split()[i], end = " ")
            print()
        elif command.split()[0] == "type":
            if command.split()[1] in ["echo", "exit", "type"]:
                print(f"{command.split()[1]} is a shell builtin.")
            else:
                for i in range (1, len(command.split())):
                    print(command.split()[i], end = " ")
                print("command not found")                                      
        else:
            print(f"{command}: command not found") 


if __name__ == "__main__":
    main()