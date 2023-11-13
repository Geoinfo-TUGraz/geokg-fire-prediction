import requests
from dotenv import load_dotenv
import os

load_dotenv()

GRAPHDB_BASE_URL = os.getenv("GRAPHDB_BASE_URL")
REPO_ID = os.getenv("REPO_ID")
GRAPHDB_USERNAME = os.getenv("GRAPHDB_USERNAME")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")


def execute_query(query: str) -> dict:
    """query GraphDB reporsitory"""

    url = f"{GRAPHDB_BASE_URL}/repositories/{REPO_ID}"
    headers = {
        "Content-Type": "application/sparql-query",
        "Accept": "application/sparql-results+json"
    }

    response = requests.post(url, headers=headers, auth=(
        GRAPHDB_USERNAME, GRAPHDB_PASSWORD), data=query)
    print(response.url)
    response.raise_for_status()
    return response.json()


def upload_data(path_to_ttl_file: str) -> None:
    """upload ttl file to default graph in repository"""

    url = f"{GRAPHDB_BASE_URL}/repositories/{REPO_ID}/rdf-graphs/service?default"
    headers = {
        "Content-Type": "text/turtle"
    }

    with open(path_to_ttl_file, "rb") as ttl_data:
        print(ttl_data)
        response = requests.post(url, data=ttl_data, headers=headers, auth=(
            GRAPHDB_USERNAME, GRAPHDB_PASSWORD))
        if response.status_code == 200:
            print("TTL file uploaded successfully")
        else:
            print(
                f"Failed to upload TTL file. Status code: {response.status_code}")
            print(response.text)


if __name__ == "__main__":

    path_to_fire_cells_subset = r"../../data/fire_data_subset/fire_cells.ttl"
    upload_data(path_to_fire_cells_subset)

    '''
    # execute query
    query = """
    SELECT ?s ?p ?o 
    WHERE {
        ?s ?p ?o
    } LIMIT 10
    """

    result = execute_query(query)
    print(result)
    '''
