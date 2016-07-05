#!/usr/bin/bash


BROKERS="{{ brokers }}"


if [ -z "$1" ]; then
    let START="$(date +%m)-1"
else
    let START=$1
fi

if [ -z "$2" ]; then
    let END="$(date +%m)"
else
    let END=$2
fi


for broker in $BROKERS;do

    for cmd in bids tenders invoices refunds; do
        echo "Generating ${cmd} for ${broker}"
        {{parts.buildout.directory}}/bin/"$cmd" -b "$broker" -p "0${START}-01" "0${END}-01"
    done

    passwd=$(pass zip/$broker)
    echo "Creating zip file with bids and invoices for ${broker}"
    find {{parts.buildout.directory}}/var/reports/  | grep "${broker}@0${START}-01--0${END}-01-\(bids\|invoices\).csv" | xargs -L 2 {{parts.buildout.directory}}/bin/zip -p "$passwd" -f 

done
