#!/usr/bin/env fish

# Install shell scripts to ~/.local/bin by symlinking them from the repo

set -l script_dir (realpath (dirname (status -f)))
set -l this (realpath (status -f))

for script in (fd -tx . $script_dir)
    set -l src (realpath $script)
    if test $src = $this
        continue
    end

    set -l dst ~/.local/bin/,(path change-extension '' (basename $script))
    echo $src '->' $dst
    ln -s $src $dst
end

echo
echo "Scripts symlinked to ~/.local/bin. Ensure that directory is in your PATH."
echo "You're responsible for cleaning up any removed or renamed scripts."
echo "To uninstall, remove the symlinks from ~/.local/bin."
