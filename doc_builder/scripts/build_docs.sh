#!/bin/bash

# exit on error
set -e

for i in "$@"
do
case $i in
    -u=*|--url=*)
    URL="${i#*=}"
    shift # past argument=value
    ;;
    -p=*|--url-path=*)
    URLPATH="${i#*=}"
    shift # past argument=value
    ;;
    -s=*|--source=*)
    SOURCE="${i#*=}"
    shift # past argument=value
    ;;
    -o=*|--output=*)
    OUTPUT="${i#*=}"
    shift # past argument=value
    ;;
    *)
          # unknown option
    ;;
esac
done

echo "---------------------------------------------------"
echo "DOC BUILD"
echo "Source = ${SOURCE}"
echo "Output = ${OUTPUT}"
echo "Url    = ${URL}${URLPATH}"
echo "---------------------------------------------------"

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

TMP_BUILD_FOLDER=${THIS_DIR}/_build
WEBSITE_FOLDER=${OUTPUT}

echo "cleaning out build location"
rm -rf ${TMP_BUILD_FOLDER}/_build

echo "creating build location"
mkdir ${TMP_BUILD_FOLDER}
mkdir ${TMP_BUILD_FOLDER}/markdown_src

echo "copying markdown docs scaffold into build locatio"
cp -r ${SOURCE}/* ${TMP_BUILD_FOLDER}/markdown_src

echo "cloning core..."
git clone --depth 1 https://github.com/shotgunsoftware/tk-core.git ${TMP_BUILD_FOLDER}/git/tk-core
export PYTHONPATH=$PYTHONPATH:${TMP_BUILD_FOLDER}/git/tk-core/python

echo "converting sphinx -> markdown"
sphinx-build -b markdown -c ${THIS_DIR}/../sphinx -D project='foo' -D release='bar' -D version='0.0.0' ${TMP_BUILD_FOLDER}/git/tk-core/docs ${TMP_BUILD_FOLDER}/markdown_src/tk-core

echo "building jekyll site"
BUNDLE_GEMFILE=${THIS_DIR}/../Gemfile JEKYLL_ENV=production bundle exec jekyll build --baseurl ${URLPATH} --config ${THIS_DIR}/../jekyll/_config.yml --source ${TMP_BUILD_FOLDER}/markdown_src --destination ${OUTPUT}


echo "------------------------------------------------------"
echo "Build completed."
echo "------------------------------------------------------"

