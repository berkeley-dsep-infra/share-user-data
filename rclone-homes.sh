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
    exists=$(rclone lsf ${rclone_target}:"${folder}"/${f} 2>/dev/null)
    exists_md5=$(rclone lsf ${rclone_target}:"${folder}"/${f}.md5sum 2>/dev/null)
	# we don't do anything if both tarball and md5 exist in the cloud
    if [ ! -z "${exists}" -a ! -z "${exists_md5}" ]; then
        echo $d already uploaded
        continue
    fi
    if [ ! -f $f ]; then
        echo creating $f
        tar -c -z --exclude=.git --exclude=.gz --exclude=.zip --exclude=.nii -f $f ${d}
		# update md5sum whenever we make the tarball
		md5sum $f > ${f}.md5sum
    fi
    if [ ! -f $f ]; then
        echo error $d
        continue
    fi
    echo copying $d
    rclone copy $f ${f}.md5sum ${rclone_target}:"${folder}"/
    if [ $? -eq 0 ]; then
        rm -f $f ${f}.md5sum
    else
        echo error copying $f
    fi
done
