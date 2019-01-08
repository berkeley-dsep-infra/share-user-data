#!/bin/bash

# Given a folder of hub home directories, compress and upload them to a
# rclone destination. Requires that rclone has already been configured.

folder="2018 Fall Data100"
rclone_target="bdrive"

cd /export/pool0/homes

if [ -z "$1" ]; then
    dirlist=$(ls -d *)
else
    dirlist=$*
fi

for d in ${dirlist} ; do
    if [ ! -d $d ]; then continue ; fi
    echo $d
    f=${d}.tar.gz
    exists=$(rclone lsf ${rclone_target}:"${folder}"/${d}.tar.gz 2>/dev/null)
    if [ ! -z "${exists}" ]; then
        echo $d already uploaded
        continue
    fi
    if [ ! -f $f ]; then
        echo creating $f
        tar -c -z --exclude=.git --exclude=.gz --exclude=.zip --exclude=.nii -f $f ${d}
    fi
    if [ ! -f $f ]; then
        echo error $d
        continue
    fi
    echo copying $d
    rclone copy $f ${rclone_target}:"${folder}"/
    if [ $? -eq 0 ]; then
        rm -f $f
    else
        echo error copying $f
    fi
done
