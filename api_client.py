# api_client.py
"""
API client for fetching data from PokéAPI
"""

import requests
from typing import Dict, Any, Optional
from config import POKEMON_BASE_URL, SPECIES_BASE_URL

class PokeAPIClient:
    """Handles all API communication with PokéAPI"""
    
    def __init__(self):
        self.base_url = POKEMON_BASE_URL
        self.species_url = SPECIES_BASE_URL
    
    def get_pokemon_data(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Fetch Pokemon data from PokéAPI"""
        try:
            # Convert to lowercase for API consistency
            query = str(name_or_id).lower().strip()

            # Get basic Pokemon data
            response = requests.get(f"{self.base_url}{query}")
            if response.status_code != 200:
                return None

            pokemon_data = response.json()

            # Get species data for description, egg groups, growth rate
            species_response = requests.get(f"{self.species_url}{pokemon_data['id']}")
            species_data = species_response.json() if species_response.status_code == 200 else {}

            # Get ability descriptions
            abilities_data = []
            for ability in pokemon_data.get('abilities', []):
                ability_url = ability['ability']['url']
                ability_response = requests.get(ability_url)
                if ability_response.status_code == 200:
                    abilities_data.append(ability_response.json())

            return {
                'pokemon': pokemon_data,
                'species': species_data,
                'abilities_detail': abilities_data
            }
        except requests.RequestException:
            return None
    
    def get_move_details(self, move_url: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed move information"""
        try:
            response = requests.get(move_url)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    def get_location_encounters(self, pokemon_data: Dict[str, Any]) -> Optional[list]:
        """Fetch location encounter data for a Pokemon"""
        try:
            location_url = pokemon_data.get('location_area_encounters')
            if not location_url:
                return []
            
            response = requests.get(location_url)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    def get_location_area_details(self, area_url: str) -> Optional[Dict[str, Any]]:
        """Fetch location area details"""
        try:
            response = requests.get(area_url)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    def get_location_details(self, location_url: str) -> Optional[Dict[str, Any]]:
        """Fetch location details"""
        try:
            response = requests.get(location_url)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None