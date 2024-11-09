from flask import Flask, jsonify
import os
from elasticsearch import Elasticsearch, helpers
import requests

app = Flask(__name__)

# Connect to Elasticsearch with authentication
try:
    es = Elasticsearch(
        "http://elasticsearch:9200",
        basic_auth=("elastic", os.environ.get('ELASTIC_PASSWORD'))
    )
    if es.ping():
        print("Connected to Elasticsearch")
    else:
        print("Failed to connect to Elasticsearch")
except Exception as e:
    print(f"Error connecting to Elasticsearch: {e}")

# Define the index name
index_name = "nobel_prizes"

# Create the index if it doesn't already exist
if not es.indices.exists(index=index_name):
    # Configure the mappings for the dataset
    mapping = {
        "mappings": {
            "properties": {
                "year": {"type": "integer"},
                "category": {"type": "text"},
                "laureates": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "integer"},
                        "firstname": {"type": "text"},
                        "surname": {"type": "text"},
                        "motivation": {"type": "text"},
                        "share": {"type": "integer"}
                    }
                }
            }
        }
    }
    print(f"Creating index '{index_name}'")
    es.indices.create(index=index_name, body=mapping)

    # Load data from API and insert into Elasticsearch
    try:
        response = requests.get("https://api.nobelprize.org/v1/prize.json")
        response.raise_for_status()
        data = response.json()["prizes"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        exit(1)  # Exit the program

    actions = [
        {
            "_index": index_name,
            "_source": record
        }
        for record in data
    ]
    helpers.bulk(es, actions)


# --- HELPER FUNCTIONS START --- #

# Perform a fuzzy search on the index
def fuzzy_search(index_name, query_fields, fuzziness="AUTO"):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {field: {"query": query_fields[field], "fuzziness": fuzziness}}} for field in query_fields
                ]
            }
        }
    }
    response = es.search(index=index_name, body=query)
    return response['hits']['hits']

def fuzzy_search_nested(path, index_name, query_fields, fuzziness="AUTO"):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"nested": {
                        "path": path,
                        "query": {
                            "bool": {
                                "must": [
                                    {"match": {f"{path}.{field}" if path else field: {"query": query_fields[field], "fuzziness": fuzziness}}} for field in query_fields
                                ]
                            }
                        },
                        "inner_hits": {}
                    }}
                ]
            }
        }
    }
    response = es.search(index=index_name, body=query)
    return response['hits']['hits']

def create_result_list(results):
    result_list = []
    for result in results:
        result_list.append({result['inner_hits']})
    return result_list
# --- HELPER FUNCTIONS END --- #

# --- FLASK API ROUTES START --- #

@app.route('/search/firstname=<firstname>')
def get_nobel_firstname(firstname):
    query_fields = {"firstname": firstname}
    results = fuzzy_search_nested("laureates", index_name, query_fields)
    return create_result_list(results)

@app.route('/search/surname=<surname>')
def get_nobel_surname(surname):
    query_fields = {"surname": surname}
    results = fuzzy_search_nested("laureates", index_name, query_fields)
    return jsonify(create_result_list(results))


@app.route('/search/firstname=<firstname>&surname=<surname>')
def get_nobel_firstname_and_surname(firstname, surname):
    query_fields = {"firstname": firstname, "surname": surname}
    results = fuzzy_search_nested("laureates", index_name, query_fields)
    return jsonify(create_result_list(results))


@app.route('/search/category=<category>')
def get_nobel_category(category):
    query_fields = {"category": category}
    results = fuzzy_search(index_name, query_fields)
    return jsonify(create_result_list(results))


@app.route('/search/description=<description>')
def get_nobel_description(description):
    query_fields = {"motivation": description}
    results = fuzzy_search_nested("laureates", index_name, query_fields)
    return jsonify(create_result_list(results))

# --- FLASK API ROUTES END --- #

# The start the flask application in port 8000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)