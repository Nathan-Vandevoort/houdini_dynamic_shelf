#!/bin/bash
set -e

if [[ "$REZ_BUILD_TYPE" == "local" ]]
then
  cmd="ln -sfv"
else
  cmd="cp -rfv"
fi

rm -rf "$REZ_BUILD_INSTALL_PATH/python"
mkdir "$REZ_BUILD_INSTALL_PATH/python"
$cmd "$REZ_BUILD_SOURCE_PATH/dynamic_shelf" "$REZ_BUILD_INSTALL_PATH/python/"
