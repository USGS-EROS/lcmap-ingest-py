#! /bin/bash

for f in data/*.html; do
  lynx -dump -hiddenlinks=listonly -listonly $f | grep ".tar.gz" | cut -c7- | sort > $f.href
done