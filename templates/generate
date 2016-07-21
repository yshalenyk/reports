#!/usr/bin/bash


BROKERS="{{ brokers }}"


parse_date () {

    IFS='-' read -r year month day< <(echo $1)
    if [ -z $year ] || [ -z $month ] || [ -z $day ]; then
        year=$(date +'%Y')
        if [ -z $month ] && [ -z $day ]; then
            month=$1
            day="01"
        fi
        if ! [ -z $month ] && [ -z $day ]; then
            IFS='-' read -r month day< <(echo $1)
        fi
    fi

    echo $(date -d"$year-$month-$day" +'%Y-%m-%d')
}

if [ -z "$1" ]; then
    START="$(date -d'-1 month' +'%Y-%m')-01"
else
    START=$(parse_date $1)
fi

if [ -z "$2" ]; then
    END="$(date  +'%Y-%m')-01"
else
    END=$(parse_date $2)
fi


echo "Generating reports form $START to $END"
echo

for broker in $BROKERS;do

    for cmd in bids tenders invoices refunds; do
        echo "Generating ${cmd} for ${broker}"
        {{parts.buildout.directory}}/bin/"$cmd" -b "$broker" -p "$START" "$END"
    done

    for file in $(find {{parts.buildout.directory}}/var/reports/  -maxdepth 1 -regex "{{parts.buildout.directory}}/var/reports/$broker@$START--$END-\(tenders\|refunds\).csv"); do
        mv "$file" "${file}_contracts.csv"
    done

    for status in cancelled unsuccessful; do

        for cmd in tenders refunds; do 
            {{parts.buildout.directory}}/bin/"$cmd" -b "$broker" -p "$START" "$END" --status one="$status"
        done

        for file in $(find {{parts.buildout.directory}}/var/reports/  -maxdepth 1 -regex "{{parts.buildout.directory}}/var/reports/$broker@$START--$END-\(tenders\|refunds\).csv"); do
            mv "$file" "${file}_${status}.csv"
        done

    done


    passwd=$(pass {{ zip_path }}/$broker)
    echo "Creating zip file with bids and invoices for ${broker}"
    find {{parts.buildout.directory}}/var/reports/  -maxdepth 1 -regex "{{parts.buildout.directory}}/var/reports/$broker@$START--$END-\(invoices\|bids\).csv"  | xargs -L 2 {{parts.buildout.directory}}/bin/zip -p "$passwd" -f 

done


echo "Creating zip archive with refunds"
find {{parts.buildout.directory}}/var/reports/ -maxdepth 1 -regex ".*@$START--$END-\(tenders\|refunds\).*.csv" | xargs bin/zip -z "$START-$END-tender-refunds.zip" -f
