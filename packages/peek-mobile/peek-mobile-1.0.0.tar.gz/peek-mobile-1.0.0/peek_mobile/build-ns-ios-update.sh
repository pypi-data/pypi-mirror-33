#!/usr/bin/env bash

DIR_NAME="`dirname $0`"
cd $DIR_NAME

DIR_NAME=`pwd`


cd build-ns && tns build ios

cd platforms/ios/buildns && zip -r -9 $DIR_NAME/app_ios.zip app

