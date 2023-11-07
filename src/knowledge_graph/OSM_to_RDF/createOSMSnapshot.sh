# Install Osmosis on Mac
brew install osmosis

# Extracting the features contained in a bounding polygon from an .osm.pbf file
osmosis --read-pbf file=../../../data/R01_austria/austria-latest.osm.pbf --bounding-polygon file=../../../data/testarea/aoi_WGS84.poly --write-pbf file=../../../data/testarea/testarea.osm.pbf
