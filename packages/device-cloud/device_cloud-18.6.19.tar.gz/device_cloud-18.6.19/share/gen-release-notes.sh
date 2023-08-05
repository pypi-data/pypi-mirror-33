#!/bin/sh
tag1=$1
tag2=$2
echo git log ${tag1}..${tag2} |grep -v "^commit"|grep -v "^Author"|grep -v "^Signed-off-by"|grep -v "^Date" 
git log ${tag1}..${tag2} |grep -v "^commit" 
