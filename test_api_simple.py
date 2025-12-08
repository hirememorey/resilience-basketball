"""
Simple test of HoopsHype GraphQL API
"""
import requests
import json

# Test the API directly
api_url = "https://www.hoopshype.com/api/data/"

query = """
query ContractsSalariesPlayersIndexPage(
    $season: Int!
    $size: Int!
    $cursor: String
) {
    contracts(
        season: $season
        size: $size
        cursor: $cursor
    ) {
        numResults
        cursor
        contracts {
            playerID
            playerName
            seasons {
                salary
                season
            }
        }
    }
}
"""

variables = {
    "season": 2024,
    "size": 20,
    "cursor": None
}

payload = {
    "query": query,
    "variables": variables,
    "operationName": "ContractsSalariesPlayersIndexPage"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Content-Type': 'application/json'
}

print("Testing HoopsHype GraphQL API...")
print(f"URL: {api_url}")
print(f"Season: 2024")

# Try GET with query parameters (as shown in the original URL)
import urllib.parse
query_str = urllib.parse.quote(query)
vars_str = urllib.parse.quote(json.dumps(variables))
op_name = "ContractsSalariesPlayersIndexPage"

get_url = f"{api_url}?query={query_str}&variables={vars_str}&operationName={op_name}"

print(f"\nTrying GET request...")
try:
    response = requests.get(get_url, headers=headers, timeout=30)
    print(f"GET Status: {response.status_code}")
except Exception as e:
    print(f"GET failed: {e}")

# Also try POST
print(f"\nTrying POST request...")
try:
    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if 'errors' in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
        else:
            contracts_data = data.get('data', {}).get('contracts', {})
            contracts = contracts_data.get('contracts', [])
            
            print(f"✅ Success! Found {len(contracts)} contracts")
            print(f"   Total results: {contracts_data.get('numResults', 'N/A')}")
            print(f"   Cursor: {contracts_data.get('cursor', 'None')}")
            
            if contracts:
                print("\nSample contracts:")
                for i, contract in enumerate(contracts[:5], 1):
                    player_name = contract.get('playerName', 'N/A')
                    player_id = contract.get('playerID', 'N/A')
                    seasons = contract.get('seasons', [])
                    
                    print(f"\n{i}. {player_name} (ID: {player_id})")
                    for season_data in seasons[:2]:  # Show first 2 seasons
                        salary = season_data.get('salary', 0)
                        season = season_data.get('season', 'N/A')
                        if salary:
                            print(f"   - {season}: ${salary/1_000_000:.2f}M")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

