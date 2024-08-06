# documentation

## parse_metadata.yml

`parse_metdata.py` references paths for you machine in `parse_metadata.yml`. 
Here are the example values on my machine:

- `xmldir`: /Users/marcp/Desktop/metadata/xml
- `srcdir`: /Users/marcp/Desktop/metadata
- `finalyaml`: /Users/marcp/Desktop/metadata.yml

When you run `parse_metadata.py` for the first time it will print the path for `parse_metadata.yml`.

## file layout of website

- each person has a folder named after their ID
- {id}/index.html is the main display for that person
- {id}/{id}.jpg is the designated thumbnail for that person
- Images are {id}/YYYYMMDDNN{id}.jpg where NN is an index that starts at 00
- Images named {id}/+YYYYMMDDNN{id}.jpg is a full resoltion image
- Images without the leading + are the thumbnails
- type=href has a sub-dir (`folder`)
