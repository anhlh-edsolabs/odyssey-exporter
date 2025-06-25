"""Aptos Pongz NFTs extractor
Usage:
python main.py
"""
import argparse
import csv
import json
import time
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Aptos Mainnet API base URL
BASE_URL = "https://api.mainnet.aptoslabs.com/v1"
# Aptos Indexer GraphQL API
INDEXER_URL = "https://indexer.mainnet.aptoslabs.com/v1/graphql"

# Configure retries
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

# GraphQL query to fetch all transactions for an account
GRAPHQL_QUERY = """
query GetTokens($collection_id: String!, $limit: Int!, $offset: Int!) {
    current_collections_v2(
        where: { collection_id: { _eq: $collection_id } }
    ){
        current_supply
    }
    current_token_ownerships_v2(
        where: { current_token_data: { collection_id: { _eq: $collection_id } } }
        limit: $limit
        offset: $offset
    ) {
        token_data_id,
        current_token_data {
            token_name,
            token_uri,
            token_properties
        }
        owner_address
    }
}
"""

# Step 1: Query Indexer API for tokens in the collection
def fetch_tokens_in_collection(collection_id):
    """Fetch tokens in the collection."""
    tokens = []
    offset = 0
    limit = 100  # Adjust based on API limits
    token_count = 0 # Counter for the number of tokens fetched

    while True:
        variables = {
            "collection_id": collection_id,
            "limit": limit,
            "offset": offset
        }
        payload = {"query": GRAPHQL_QUERY, "variables": variables}
        try:
            response = session.post(INDEXER_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                print(f"GraphQL errors: {data['errors']}")
                break
            token_ownerships = data["data"]["current_token_ownerships_v2"]
            if not token_ownerships:
                break  # No more tokens to fetch
            
            token_supply = data["data"]["current_collections_v2"][0]["current_supply"]
            
            for token in token_ownerships:
                print(f"Token {token_count}: {token['token_data_id']}-{token['current_token_data']['token_name']} of {token_supply}")
                tokens.append({
                    "token_data_id": token["token_data_id"],
                    "token_name": token["current_token_data"]["token_name"],
                    "owner": token["owner_address"],
                    "token_uri": token["current_token_data"]["token_uri"],
                    "properties": token.get("current_token_data", {}).get("token_properties", {})
                })
                token_count += 1
            offset += limit
            time.sleep(5)  # Avoid hitting rate limits
        except requests.exceptions.RequestException as e:
            print(f"Error querying Indexer: {e}")
            break
    return tokens

# Step 2: Export to CSV
def export_to_csv(tokens, filename):
    """Export to CSV"""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["token_data_id", "token_name", "owner", "properties"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for token in tokens:
            writer.writerow(token)
    print(f"Exported {len(tokens)} tokens to {filename}")

def export_to_json(tokens, filename):
    """Export to JSON"""
    try:
        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(tokens, jsonfile, indent=4)
        print(f"Exported {len(tokens)} tokens to {filename}")
    except (IOError, TypeError) as e:
        print(f"Error exporting to JSON: {e}")

# Main execution
def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Fetch Aptos NFT collection data.")
    parser.add_argument("collection_id", help="The collection ID (Object address) to fetch.")
    parser.add_argument(
        "-o",
        "--output",
        default="tokens",
        help="Output file name without the extension.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output file format (json or csv). Defaults to json.",
    )
    args = parser.parse_args()

    # Fetch tokens using Indexer
    print(f"Fetching tokens for collection ID: {args.collection_id}")
    tokens = fetch_tokens_in_collection(args.collection_id)
    if not tokens:
        print("No tokens found. Verify the collection ID or check the Indexer API.")
        return
    print(f"Found {len(tokens)} tokens")

    # Export to file
    filename = f"{args.output}.{args.format}"
    if args.format == 'csv':
        export_to_csv(tokens, filename)
    else:
        export_to_json(tokens, filename)

if __name__ == "__main__":
    main()
