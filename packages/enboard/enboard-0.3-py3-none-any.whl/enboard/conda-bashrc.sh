if [[ -f /etc/bash.bashrc ]]; then
  source /etc/bash.bashrc
fi
if [[ -f ~/.bashrc ]]; then
  source ~/.bashrc
fi

# The parts below are copied from conda's own activate script
# if CONDA_DEFAULT_ENV not in PS1, prepend it with parentheses
if [[ $("conda" ..changeps1) == "1" ]]; then
    if ! $(grep -q CONDA_DEFAULT_ENV <<<$PS1); then
        export PS1="(${CONDA_DEFAULT_ENV}) $PS1"
    fi
fi

# Load any of the scripts found $PREFIX/etc/conda/activate.d AFTER activation
_CONDA_D="${CONDA_PREFIX}/etc/conda/activate.d"
if [[ -d "$_CONDA_D" ]]; then
    IFS=$(echo -en "\n\b")&>/dev/null  && for f in $(find "$_CONDA_D" -iname "*.sh"); do source "$f"; done
fi
