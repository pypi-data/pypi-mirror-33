#!/bin/bash
# vim:ts=4
#
# Handle static data required by Bootini Star, namely EVE Online
# item groups and item types.

dbname="$1"
if [ -z "$dbname" ]; then
    echo "Usage: $(basename $0) {dbname}" >&2
    exit 1
fi

for table in groups types; do
    echo "bzcat $table.json.bz2 | mongoimport -d $dbname -c eve_$table --drop"
done
