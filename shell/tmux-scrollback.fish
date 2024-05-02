#!/usr/bin/env fish

argparse 't/target=' h/help e/edit -- $argv; or exit 1

if set -q _flag_help
    echo "Usage: $(basename (status -f)) [-t TARGET] [-e] [FILE]"
    echo
    echo "Open the scrollback buffer in an editor."
    echo
    echo "Options:"
    echo "  -t, --target TARGET  The target pane number to capture from. If absent, use the current one."
    echo "                       Get it from `PREFIX q` (default: C-s q)."
    echo "  -e, --edit           Edit the file in a new window."
    echo "  -h, --help           Display this help message."
    return 1
end

if not set -q argv[1]
    echo "FILE is required. Use -h/--help for help."
    exit 1
end
set file $argv[1]

set -l opt
if set -q _flag_target
    set -l opt -t $_flag_target
end

tmux capture-pane -pS- $opt >$file
echo Saved to $file
if set -q _flag_edit
    tmux new-window "$EDITOR $file"
end
