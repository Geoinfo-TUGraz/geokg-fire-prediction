# geokg-fire-prediction

This repository contains the code for utilizing a GeoKnowledge Graph and ML for wildfire prediction in Austria.

### Set-Up

Creat an .env file in the project root directoy and define variables for GraphDB connection

```
GRAPHDB_BASE_URL=http://<IP>:<Port>
REPO_ID=<GrahpDB Repo>
GRAPHDB_USERNAME=<GraphDB Username>
GRAPHDB_PASSWORD<GraphDB PW>
```

### TODOs

- Refactoring and Cleanup of _transform_fire_data_to_rdf.py_ file
- Upload of fire data turtle file (subset) to GraphDB
- Upload of worldkg graph subset to GraphDB
- Create connections between fire cells and osm entities
- GNN Development
