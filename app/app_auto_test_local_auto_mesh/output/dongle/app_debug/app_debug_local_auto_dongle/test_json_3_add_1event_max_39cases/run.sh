#!/bin/bash

file=$1
num=$2

if [ "$2" == "" ];then
    echo "input the file and num, then will copy it num times"
    exit
fi

for ((autoid=1;autoid<num;autoid++)) 
do
    echo $autoid
 
    cp $file $autoid$file
    sed -i 's:"id".*:"id"\:"'$autoid'",:g' $autoid$file
done

rm $file
