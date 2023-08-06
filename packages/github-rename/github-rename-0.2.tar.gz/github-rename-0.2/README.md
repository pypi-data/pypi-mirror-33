# GitHub-rename
A helper to change .git origin url after renaming your GitHub id.

## Install

```terminal
pip install github-rename
```

## Usage
### Example
Change from qiugits to qqghst.

```terminal
$ github-rename -f qiugits -t qqghst
Searching for ./.git/config...
Replaced line(s):

        url = https://github.com/qiugits/GitHub-rename.git
->      url = https://github.com/qqghst/GitHub-rename.git


Matched and replaced 1 time(s).

./.gitmodules does not exist.
```

```terminal
$ github-rename -h
Usage: github-rename [OPTIONS]

  GitHub-rename

  This cli tool helps you to rename your github urls
  in .git/config and .gitmodules.

  Please help us improve by opening issues
  in https://github.com/qqghst/GitHub-rename

Options:
  -f, --from TEXT   Name to change from.
  -t, --to TEXT     Name to change to.
  --bak / --no-bak  Make .bak file for backup. (Defalult is True)
  --version         Show the version and exit.
  -h, --help        Show this message and exit.
```

