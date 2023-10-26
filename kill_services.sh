#!/bin/bash

echo "killing VIM-BCAST/PARLL services..."
for pid in $(pgrep -f 'main_.*.py'); do kill $pid; done
echo "done"