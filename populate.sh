#!/bin/bash
# CLI: --server <server> --token <token>
set -e
# Check if the required arguments are provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 --server <server> --token <token>"
    exit 1
fi
# Parse the arguments
# Use getopt for argument parsing
if ! PARSED_ARGS=$(getopt -o "" --long server:,token: -- "$@"); then
    echo "Error: Invalid arguments"
    exit 1
fi
eval set -- "$PARSED_ARGS"

while true; do
    case "$1" in
        --server)
            server="$2"; shift 2 ;;
        --token)
            token="$2"; shift 2 ;;
        --)
            shift; break ;;
        *)
            echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

# Validate required arguments
if [ -z "$server" ]; then
    echo "Error: --server requires a non-empty value"
    exit 1
fi
if [ -z "$token" ]; then
    echo "Error: --token requires a non-empty value"
    exit 1
fi

export BASE_URL="$server"
export API_KEY="$token"

for repo in cflp etsp flp cvrp_2d job_shop knapsack; do
    cd ./REPOSITORY/$repo
    python populate.py
    cd - > /dev/null
done

# Delete the environment variables
unset BASE_URL
unset API_KEY
