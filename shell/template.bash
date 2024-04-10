#!/bin/bash
set -euo pipefail;

SCRIPT_NAME="$(basename "$0")"

log() {
  local -r level="$1"
  local -r message="$2"
  local -r timestamp=$(date +"%Y-%m-%d %H:%M:%S")

  >&2 echo -e "${timestamp} [${level}] [$SCRIPT_NAME] ${message}"
}

assert_not_empty() {
  local -r arg_name="$1"
  local -r arg_value="$2"

  if [[ -z "$arg_value" ]]; then
    log "ERROR" "The value for '$arg_name' cannot be empty"
    exit 1
  fi
}

assert_is_installed() {
  local -r name="$1"

  if [[ ! $(command -v "$name") ]]; then
    log "ERROR" "The binary '$name' is required by this script but is not installed or in the system's PATH."
    exit 1
  fi
}

print_usage() {
  echo
  echo "Usage: $SCRIPT_NAME [OPTIONS]"
  echo
  echo "This script creates a new certiticate, and it installs it into the right namespace"
  echo
  echo "Options:"
  echo
  echo -e "  --namespace\tThe namespace to install the certificate in"
  echo -e "  --suffix\tAn optional suffix for the hostname"
  echo -e "  --dry-run\tDon't install the certificate"
  echo
  echo "Example:"
  echo
  echo "  $SCRIPT_NAME --namespace test --dry-run"
}

run() {
  local namespace=""
  local suffix=""
  local dry_run="false"

  while [[ $# -gt 0 ]]; do
    local key="$1"

    case "$key" in
      --namespace)
        namespace="$2"
        shift
        ;;
      --suffix)
        assert_not_empty "$key" "$2"
        suffix="$2"
        shift
        ;;
      --dry-run)
        dry_run="true"
        ;;
      --help)
        print_usage
        exit
        ;;
      *)
        log "ERROR" "Unrecognized argument: $key"
        print_usage
        exit 1
        ;;
    esac

    shift
  done

  # mandatory flag validation
  assert_not_empty "--namespace" "$namespace"

  # make sure tools are installed
  assert_is_installed "vault"
  assert_is_installed "openssl"
  assert_is_installed "jq"

  # do the work!
  local -r cert=$(generate_cert "$suffix")

  store_cert "$namespace" "$cert" "$dry_run"

}

run "$@"
