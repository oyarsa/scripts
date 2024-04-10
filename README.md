# scripts

Repository for random scripts that I write over time.

Mostly Python things, which are collected in a single project and installed as package.
The project is maintained with PDM and installed with pipx, so each individual script
can be run as a standalone command.

## Installation

```bash
> git clone git@github.com:oyarsa/scripts.git
> pipx install --editable scripts/python
```

Scripts should be named with a lead `-` (e.g. `-ntok`) so that they are easy to find in
the shell.

