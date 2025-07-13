#!/bin/bash
#

#
# Converts notebooks to .py files for testing.

readonly SCRIPT_DIR="$( cd "$( dirname "$0" )" &> /dev/null && pwd )"
readonly EXAMPLES_DIR="${SCRIPT_DIR}"/../examples
readonly OUTPUT_DIR="$1"
readonly TEMP_DIR="$(mktemp -d)"


function find_notebooks() {
  find "${EXAMPLES_DIR}" -type f -iname '*.ipynb'
}


function collect_notebooks() {
  for file in $(find_notebooks); do
    echo "Copying ${file} to ${TEMP_DIR}"
    cp "${file}" "${TEMP_DIR}"
  done
}


function disable_ipython_magic() {
  local start_of_line='^\s*\"\s*'
  local match="\(${start_of_line}\)\([%!]\)"
  local replacement='\1pass  # \2'
  for file in "${TEMP_DIR}"/*; do
    echo "Disabling ipython magic in ${file}"
    sed -i "s/${match}/${replacement}/g" "${file}"
  done
}


function convert_notebooks() {
  jupyter nbconvert --to=python --output-dir="${OUTPUT_DIR}" "${TEMP_DIR}"/*
}


function main() {
  collect_notebooks \
  && disable_ipython_magic \
  && convert_notebooks \
  && ls "${OUTPUT_DIR}"
}


main >&2
