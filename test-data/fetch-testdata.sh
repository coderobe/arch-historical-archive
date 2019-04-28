#!/bin/bash

set -e

cd "$(dirname "$0")"
rsync -Pratv --include-from ./include-list orion:/srv/archive/ archive/
