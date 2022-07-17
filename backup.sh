#!/bin/sh

# backup.sh --- Automatic backup script utilizing Rabbit
#
# A list of patterns (one per line, wildcards allowed) to backup is expected
# in 'CONFIG.txt'. Blank lines are allowed for organization.
#
# The token used for authenticating with GitHub is expected in 'TOKEN.txt'.

PREFIX="Depot_$(date +"%Y%m%d_%H%M")"
ARCHIVE="$PREFIX.tar.xz"

xargs ./rabbit.py -t $(cat TOKEN.txt) -p "$PREFIX" < CONFIG.txt && \
	tar -cvJf "$ARCHIVE" "$PREFIX" && \
	rm -fr "$PREFIX"
