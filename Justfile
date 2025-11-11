@default:
    just help

help:
    #!/usr/bin/env sh
    {{sh_init}}
    echo_title "General recipes:"
    echo_default "help                 Show this message."
    echo_default "format               Format data_provider code with ruff. Example usage:"
    echo_highlight "                         just format"
    echo_default "                       format specific file:"
    echo_highlight "                         just format <FilePathRelativeToProjectRoot>"
    echo_default "check                Verify the application code compliance against ruff, and mypy checks."
    echo_default "test                 Run the test suite. Example usage:"
    echo_default "                       run all tests:"
    echo_highlight "                         just test"
    echo_default "                       run specific test or tests:"
    echo_highlight "                         just test ./tests"
    echo_highlight "                         just test ./tests/test_something.py"
    echo_highlight "                         just test ./tests/test_something.py::test_it"
    echo_default "all                  format + check + test."
    echo_default "pre_commit           Run pre-commit for all files to check if all checks/tests pass."
    echo_title "Other recipes:"
    echo_default "coverage_report      Open coverage report with default browser."

init:
    #!/usr/bin/env sh
    {{sh_init}}
    init_project

# example usage:
#   just format
#   just format test.py
#   just format test.py F841,I001
default_target := './'
default_ignore := ''
format target=default_target ignore=default_ignore:
    #!/usr/bin/env sh
    {{sh_init}}
    format_code {{target}} {{ignore}}

check:
    #!/usr/bin/env sh
    {{sh_init}}
    check_code

pre_commit:
    pre-commit run --all-files

default_test_path := './tests'
default_opts        := ''
test test_path=default_test_path opts=default_opts:
    #!/usr/bin/env sh
    {{sh_init}}
    test_code {{test_path}} {{opts}}

format_and_check: format check
all: format check test

meow:
    #!/usr/bin/env sh
    {{sh_init}}
    make_me_owner_of_this_folder

clean_pycached:
    #!/usr/bin/env sh
    {{sh_init}}
    clean_pycached

coverage_report:
    #!/usr/bin/env sh
    {{sh_init}}
    open_coverage_report


# Just global variables

set dotenv-load

alias f     := format
alias c     := check
alias t     := test
alias fc    := format_and_check
alias a     := all
alias cr    := coverage_report
alias pc    := pre_commit

TITLE       := '\033[94m\033[1m'
HIGHLIGHT   := '\033[93m\033[1m'
WARNING     := '\033[91m\033[1m'
DEFAULT     := '\033[0m'

sh_init := "set -e && PROJECT_DIR=$(pwd) && . $PROJECT_DIR/justscripts/main.sh"
