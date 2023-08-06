import sys

name = "github-rename"


def main():
    from .clidriver import main
    sys.exit(main())


if __name__ == '__main__':
    main()
