#!/bin/bash

set -x
git config user.name github-actions[bot]
git config user.email 41898282+github-actions[bot]@users.noreply.github.com
git add omoikane.pickle
git commit -m "Update omoikane.pickle"
git push -f


