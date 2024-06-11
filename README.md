# scripts

Repository for random scripts that I write over time.

Mostly Python things, which are collected in a single project and installed as package.
The project is maintained with PDM and installed with pipx, so each individual script
can be run as a standalone command.

There are also some shell scripts, which depend on the fish shell. These are installed
by symlinking them to the `~/.local/bin` directory. There are few of these, since
most are functions in the Fish configuration, which is maintained with chezmoi in
the [dotfiles](https://github.com/oyarsa/dotfiles) repository.

## Installation

Requirements:
- Python 3.10
- Fish shell

```bash
> git clone git@github.com:oyarsa/scripts.git
> pipx install --editable scripts/python
> ./shell/install.fish
```

Scripts should be named with a lead `,` (e.g. `,ntok`) so that they are easy to find in
the shell.

