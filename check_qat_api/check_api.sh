#!/bin/bash

#Location of extracted IA package 
pkgLoc=$ICP_ROOT

which nm
if [ $? -ne 0 ]
then
    echo "nm missing !! install nm and try again"
    exit 1
fi

which ctags
if [ $? -ne 0 ]
then
    echo "ctags missing !! install ctags and try again"
    exit 1
fi

if [ ! -f $pkgLoc/.libs/libqat.so ]
then
    echo "File $pkgLoc/.libs/libqat.so !! build driver and try again"
    exit 1
fi

nm $pkgLoc/.libs/libqat.so > $pkgLoc/libqat_s_symbols.txt
ctagsVer=$(ctags --version | head -1 | cut -d' ' -f3 | tr -d ',')

declare -a funcList
curgIFS=$IFS
case "$ctagsVer" in
    "5.8" | "5.9.0")
        IFS=$'\n' read -r -d '' -a funcList < <( find $pkgLoc/quickassist/include/ -name "*.h" | ctags -x --c-kinds=p -L - | cut -d' ' -f1 | uniq | grep -v CPA_BITMAP )
        ;;
    "6.0.0")    IFS=$'\n' read -r -d '' -a funcList < <( find $pkgLoc/quickassist/include/ -name "*.h" | ctags -x --kinds-c=p -L - | cut -d' ' -f1 | uniq | grep -v CPA_BITMAP )
        ;;
    *)
        echo "ctags $ctagsVer not handled"
        ;;
esac
IFS=$curIFS
test=0
for func in "${funcList[@]}"
do
    count=$(grep -c $func $pkgLoc/libqat_s_symbols.txt)
    if [ $count -lt 1 ]
    then
        echo "Function $func not implimented"
	test=1
    else
	echo $func "OK"
    fi
done

if [ ${test} -ne 0 ]; then
	exit -1
elseif
	exit 0
fi	
  
