"""
GraphQL queries for fetching collection supply and token ownership data.
"""

COLLECTION_SUPPLY_QUERY = """
query GetCollectionSupply($collection_id: String!) {
    current_collections_v2(
        where: { collection_id: { _eq: $collection_id } }
    ){
        collection_name,
        current_supply
    }
}
"""

TOKEN_OWNERSHIPS_QUERY = """
query GetTokens($collection_id: String!, $limit: Int!, $offset: Int!) {
    current_token_ownerships_v2(
        where: { current_token_data: { collection_id: { _eq: $collection_id } } }
        limit: $limit
        offset: $offset
        order_by: { current_token_data: { token_name: asc } }
    ) {
        token_data_id,
        last_transaction_version,
        current_token_data {
            token_name,
            token_uri,
            token_properties
        }
        owner_address
    }
}
""" 