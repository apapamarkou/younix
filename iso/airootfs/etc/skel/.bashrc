#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

$SHELL_GREETING

source /usr/local/share/shell/fzf-cdf.bash
source /usr/local/share/shell/aliases
eval "$(starship init bash)"



