import sys


def main():
    # sys.stdout.write("$ ")
    # pass
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == "exit":
            sys.exit()
        else:
            print(f"{command}: command not found")
    


if __name__ == "__main__":
    main()
