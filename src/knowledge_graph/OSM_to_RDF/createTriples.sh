# Create the required environment from the provided environment.yml file using the following command:
# conda env create -f environment.yml
# or with pip
# pip install -r requirements.txt

conda activate worldKG_py39

python3 createTriples.py ../../../data/testarea/testarea.osm.pbf ../../../data/testarea/testarea_wKG.ttl

conda deactivate




