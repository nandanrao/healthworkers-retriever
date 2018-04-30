#!/bin/bash

supervisord
sleep 15
PROXY_STATUS=$(supervisorctl pid proxy)

if [ $PROXY_STATUS -eq 0 -o $PROXY_STATUS -eq 1 ]; then
  echo "Proxy has failed."
  exit 1
fi

echo "SUPERVISOR: Proxy running with status ${PROXY_STATUS}."
echo "SUPERVISOR: Starting Retriever"

python ./__main__.py

exit 0
