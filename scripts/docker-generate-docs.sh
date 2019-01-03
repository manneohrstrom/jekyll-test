#!/bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

docker build ${THIS_DIR}/../doc_builder -t tk-docs && \
docker run --rm  --mount type=bind,source="${THIS_DIR}/..",target=/app tk-docs \
/app/doc_builder/scripts/build_docs.sh --url=http://localhost --url-path=/tmp/foo --source=/app/docs --output=/app/_build && \
echo "Documentation built in ${THIS_DIR}/_build/index.html"
