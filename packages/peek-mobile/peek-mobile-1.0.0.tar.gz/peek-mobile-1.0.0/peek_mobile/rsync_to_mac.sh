#!/bin/bash

rsync -avP build-ns /media/psf/stash  --exclude platforms --exclude node_modules

rsync -avP build-ns/hooks /media/psf/stash/build-ns/


