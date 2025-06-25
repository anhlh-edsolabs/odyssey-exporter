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
from graphql_queries import COLLECTION_SUPPLY_QUERY, TOKEN_OWNERSHIPS_QUERY

# Aptos Mainnet API base URL
BASE_URL = "https://api.mainnet.aptoslabs.com/v1"
# Aptos Indexer GraphQL API
INDEXER_URL = "https://indexer.mainnet.aptoslabs.com/v1/graphql"

# Configure retries
session = requests.Session()
retries = Retry(total=5, backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

# Query Indexer API for tokens in the collection
def fetch_tokens_in_collection(collection_id, verbose=False):
    """Fetch tokens in the collection."""
    # First, get the total supply
    try:
        supply_payload = {"query": COLLECTION_SUPPLY_QUERY, "variables": {"collection_id": collection_id}}
        response = session.post(INDEXER_URL, json=supply_payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "errors" in data or not data.get("data", {}).get("current_collections_v2"):
            print(
                f"GraphQL errors or no collection data: {data.get('errors', 'No data found')}")
            return []
        collection_name = data["data"]["current_collections_v2"][0]["collection_name"]
        token_supply = data["data"]["current_collections_v2"][0]["current_supply"]
        print(f"Collection {collection_name} has {token_supply} tokens. Start fetching...")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching collection supply: {e}")
        return []

    all_raw_tokens = []
    offset = 0
    limit = 100

    while True:
        variables = {
            "collection_id": collection_id,
            "limit": limit,
            "offset": offset
        }
        payload = {"query": TOKEN_OWNERSHIPS_QUERY, "variables": variables}
        try:
            response = session.post(INDEXER_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                print(f"GraphQL errors: {data['errors']}")
                break
            token_ownerships = data.get("data", {}).get(
                "current_token_ownerships_v2", [])
            if not token_ownerships:
                break  # No more tokens to fetch

            all_raw_tokens.extend(token_ownerships)
            print(
                f"Fetched {len(all_raw_tokens)} records so far...")

            offset += limit
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Error querying Indexer: {e}")
            print("Rate limit likely hit. Retrying after 30 seconds...")
            time.sleep(30)
            continue

    # Process after fetching all tokens
    if verbose:
        processed_tokens = all_raw_tokens
    else:
        grouped_tokens = {}
        for token in all_raw_tokens:
            token_id = token["token_data_id"]
            if token_id not in grouped_tokens:
                grouped_tokens[token_id] = []
            grouped_tokens[token_id].append(token)

        latest_tokens = []
        for history in grouped_tokens.values():
            history.sort(
                key=lambda t: t['last_transaction_version'], reverse=True)
            latest_tokens.append(history[0])

        # Sort final list by token name
        latest_tokens.sort(key=lambda t: t['current_token_data']['token_name'])
        processed_tokens = latest_tokens

    # Format the tokens for export
    tokens = []
    for token in processed_tokens:
        tokens.append({
            "token_data_id": token["token_data_id"],
            "last_transaction_version": token["last_transaction_version"],
            "token_name": token["current_token_data"]["token_name"],
            "owner": token["owner_address"],
            "token_uri": token["current_token_data"]["token_uri"],
            "properties": token.get("current_token_data", {}).get("token_properties", {})
        })

    # Sort by the number in the token name (e.g., "Pongz #6112")
    def get_token_number_from_name(token):
        try:
            return int(token['token_name'].split('#')[-1])
        except (ValueError, IndexError):
            # Return a large number for names that don't fit the pattern
            return float('inf')

    tokens.sort(key=get_token_number_from_name)

    return tokens

# Export to CSV
def export_to_csv(tokens, filename):
    """Export to CSV"""
    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["token_data_id", "last_transaction_version",
                          "token_name", "owner", "token_uri", "properties"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for token in tokens:
                row = token.copy()
                row["properties"] = json.dumps(row.get("properties", {}))
                writer.writerow(row)
            print(f"Exported {len(tokens)} tokens to {filename}")
    except (IOError, TypeError) as e:
        print(f"Error exporting to CSV: {e}")


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
    parser = argparse.ArgumentParser(
        description="Fetch Aptos NFT collection data.")
    parser.add_argument(
        "collection_id", help="The collection ID (Object address) to fetch.")
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
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Include all ownership history. Default is to show only the latest.",
    )
    args = parser.parse_args()

    # Fetch tokens using Indexer
    print(f"Fetching tokens for collection ID: {args.collection_id}")
    tokens = fetch_tokens_in_collection(
        args.collection_id, verbose=args.verbose)
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
