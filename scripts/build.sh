#!/bin/bash

set -e

increment_version() {
    if [[ $2 == "PATCH" ]]; then
        increment="2"
    elif [[ $2 == "MINOR" ]]; then
        increment="1"
    elif [[ $2 == "MAJOR" ]]; then
        increment="0"
    else
        echo "Invalid :( "
        exit 1
    fi

    local delimiter=.
    local array=($(echo "$1" | tr $delimiter '\n'))
    array[$increment]=$((array[$increment]+1))
    if [ $increment -lt 2 ]; then array[2]=0; fi
    if [ $increment -lt 1 ]; then array[1]=0; fi
    echo $(local IFS=$delimiter ; echo "${array[*]}")
}

if [[ -d dist ]]; then
    rm -rf dist
fi

if [[ -d whatubinup2.egg-info ]]; then
    rm -rf whatubinup2.egg-info
fi


if ! [[ -n $1 ]]; then
    echo "Please enter semver incrementation"
    exit 1
else
    if ! [[ $1 == "MAJOR"  ||  $1 == "MINOR" || $1 == "PATCH" ]]; then
        echo "Please enter either MAJOR, MINOR or PATCH"
        exit 1
    fi
fi

current_version=$(cat setup.cfg | grep "version" | awk {'print $3'})

new_version=$(increment_version $current_version $1)

sed -i.bu "s/$current_version/$new_version/g" setup.cfg
rm -rf setup.cfg.bu

# Build dist
python3 setup.py sdist

# Validate
status=$(twine check dist/*)

if [[ $status == *"PASSED"* ]]; then
    echo "twine check complete, uploading new version"
    twine upload dist/*
else
    echo "Twine check failed"
    echo "$status"
fi
