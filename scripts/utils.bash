#!/bin/bash

alias lvupy='platforms/unix_micropython'
alias rexec='rshell -p /dev/ttyUSB0'
function rosu { platforms/unix modules/$1.py; }
