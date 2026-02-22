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
        else:
            print(f"{command}: command not found") 


if __name__ == "__main__":
    main()