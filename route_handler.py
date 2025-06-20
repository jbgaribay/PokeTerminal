# route_handler.py
"""
Route/Location handler for finding Pokemon at specific locations
"""

import requests
from typing import Dict, Any, List, Optional
from display_utils import DisplayFormatter

class RouteHandler:
    """Handles looking up Pokemon found at specific routes/locations"""
    
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.formatter = DisplayFormatter()
        self.location_cache = {}
    
    def handle_route_query(self, query: str) -> None:
        """Handle route lookup queries like 'route 104 emerald'"""
        try:
            # Parse the query - expecting format like "route 104 emerald" or "route 104"
            parts = query.lower().split()
            
            if len(parts) < 2:
                print("❌ Invalid route format! Use: route <location> [game]")
                print("   Examples: 'route 104', 'route 104 emerald', 'victory road platinum'")
                return
            
            # Handle different query formats
            if parts[0] == "route":
                # Format: "route 104 emerald" or "route 104"
                if len(parts) == 2:
                    # Just "route 104"
                    route_number = parts[1]
                    location_name = f"route-{route_number}"
                    game_filter = None
                elif len(parts) >= 3:
                    # "route 104 emerald"
                    route_number = parts[1]
                    location_name = f"route-{route_number}"
                    game_filter = parts[2]
                else:
                    print("❌ Invalid route format! Use: route <number> [game]")
                    return
            else:
                # Format: "victory road platinum" or other location names
                if len(parts) == 1:
                    location_name = parts[0]
                    game_filter = None
                else:
                    # Assume last part is game, everything else is location
                    game_filter = parts[-1]
                    location_name = "-".join(parts[:-1])
            
            print(f"DEBUG: Searching for location '{location_name}' with game filter '{game_filter}'")
            
            # Search for the location
            self.search_location(location_name, game_filter)
            
        except Exception as e:
            print(f"❌ Error processing route query: {e}")
    
    def search_location(self, location_query: str, game_filter: Optional[str] = None) -> None:
        """Search for a location and display Pokemon found there"""
        try:
            print(f"🗺️ Searching for location: {location_query}")
            if game_filter:
                print(f"   Game filter: {game_filter}")
            
            # First, get all locations and find matches
            locations_data = self.get_all_locations()
            if not locations_data:
                print("❌ Could not load location data")
                return
            
            # Find matching locations
            matching_locations = self.find_matching_locations(locations_data, location_query)
            
            if not matching_locations:
                print(f"❌ No locations found matching '{location_query}'")
                self.suggest_locations(locations_data, location_query)
                return
            
            # If multiple matches, show options or pick best match
            if len(matching_locations) > 1:
                best_match = self.select_best_location_match(matching_locations, location_query)
                if best_match:
                    self.display_location_pokemon(best_match, game_filter)
                else:
                    self.show_location_options(matching_locations)
            else:
                self.display_location_pokemon(matching_locations[0], game_filter)
                
        except Exception as e:
            print(f"❌ Error searching location: {e}")
    
    def get_all_locations(self) -> Optional[List[Dict[str, Any]]]:
        """Get all available locations from the API"""
        try:
            if 'all_locations' in self.location_cache:
                return self.location_cache['all_locations']
            
            print("Loading location database...")
            
            # Try the location-area endpoint which has more detailed locations
            response = requests.get(f"{self.base_url}/location-area?limit=2000", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                locations = data.get('results', [])
                print(f"DEBUG: Loaded {len(locations)} location areas from location-area endpoint")
                self.location_cache['all_locations'] = locations
                return locations
            else:
                print(f"DEBUG: location-area endpoint failed with status {response.status_code}")
                # Fallback to regular location endpoint
                response = requests.get(f"{self.base_url}/location?limit=1000", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    locations = data.get('results', [])
                    print(f"DEBUG: Loaded {len(locations)} locations from location endpoint")
                    self.location_cache['all_locations'] = locations
                    return locations
                else:
                    return None
                
        except Exception as e:
            print(f"Error loading locations: {e}")
            return None
    
    def find_matching_locations(self, locations: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Find locations that match the query"""
        query_lower = query.lower()
        matches = []
        
        print(f"DEBUG: Looking for '{query_lower}' in {len(locations)} locations...")
        
        for location in locations:
            location_name = location['name'].lower()
            
            # Direct match
            if query_lower == location_name:
                print(f"DEBUG: Direct match found: {location_name}")
                matches.append(location)
                continue
            
            # Partial match (query in name or name in query)
            if query_lower in location_name or location_name in query_lower:
                print(f"DEBUG: Partial match found: {location_name}")
                matches.append(location)
                continue
            
            # Route number matching (e.g., "121" matches "route-121")
            if query_lower.replace('route-', '').isdigit():
                route_num = query_lower.replace('route-', '')
                if f"route-{route_num}" == location_name or route_num in location_name:
                    print(f"DEBUG: Route number match found: {location_name}")
                    matches.append(location)
                    continue
        
        print(f"DEBUG: Found {len(matches)} matches")
        if matches:
            for match in matches[:3]:  # Show first 3 matches for debugging
                print(f"DEBUG: Match: {match['name']}")
        
        return matches
    
    def select_best_location_match(self, matches: List[Dict[str, Any]], query: str) -> Optional[Dict[str, Any]]:
        """Select the best matching location from multiple matches"""
        query_lower = query.lower()
        
        # Prefer exact matches
        for match in matches:
            if query_lower == match['name'].lower():
                return match
        
        # Prefer matches that start with the query
        for match in matches:
            if match['name'].lower().startswith(query_lower):
                return match
        
        # If all else fails, return the first match
        return matches[0] if matches else None
    
    def show_location_options(self, matches: List[Dict[str, Any]]) -> None:
        """Show multiple location options to the user"""
        print("🗺️ Multiple locations found:")
        print("╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
        print("║                                            LOCATION OPTIONS                                                     ║")
        print("╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")
        
        for i, location in enumerate(matches[:10], 1):  # Limit to 10 options
            location_name = location['name'].replace('-', ' ').title()
            option_line = f"{i:2}. {location_name}"
            print(f"║ {option_line:<111} ║")
        
        print("║                                                                                                                 ║")
        print("║ Try being more specific with your search!                                                                      ║")
        print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
    
    def suggest_locations(self, locations: List[Dict[str, Any]], query: str) -> None:
        """Suggest similar locations when no exact match is found"""
        suggestions = []
        query_lower = query.lower()
        
        print(f"\n🔍 DEBUG: All {len(locations)} available locations:")
        for i, location in enumerate(locations):
            print(f"   {i+1:2}. {location['name']}")
        
        # Find locations with similar names
        for location in locations:
            location_name = location['name'].lower()
            
            # Check for partial similarities
            if any(word in location_name for word in query_lower.split('-')):
                suggestions.append(location)
            
            # Check if location name contains any digits from query
            if any(char.isdigit() for char in query_lower):
                query_digits = ''.join(c for c in query_lower if c.isdigit())
                if query_digits and query_digits in location_name:
                    suggestions.append(location)
        
        if suggestions:
            print("\n💡 Did you mean one of these?")
            for suggestion in suggestions[:10]:  # Show top 10 suggestions
                suggestion_name = suggestion['name'].replace('-', ' ').title()
                print(f"   • {suggestion_name}")
        else:
            print("\n💡 Try using one of the location names above!")
            print("   The PokeAPI uses broader location categories, not individual routes.")
            print("   Example: Try 'canalave-city' or 'eterna-forest'")
    
    def display_location_pokemon(self, location_info: Dict[str, Any], game_filter: Optional[str] = None) -> None:
        """Display Pokemon found at a specific location"""
        try:
            location_name = location_info['name']
            print(f"\n🗺️ Loading Pokemon data for {location_name.replace('-', ' ').title()}...")
            
            # For location-area endpoint, we can get the data directly
            if 'location-area' in location_info.get('url', ''):
                # This is a location-area, get its details directly
                area_data = self.get_area_details(location_info['url'])
                if not area_data:
                    print("❌ Could not load area details")
                    return
                
                # Extract Pokemon encounters from this specific area
                pokemon_encounters = self.extract_area_encounters(area_data, game_filter)
                
                if not pokemon_encounters:
                    if game_filter:
                        print(f"❌ No Pokemon encounters found for {location_name.replace('-', ' ').title()} in {game_filter.title()}")
                    else:
                        print(f"❌ No Pokemon encounters found for {location_name.replace('-', ' ').title()}")
                    return
                
                # Display the results
                self.display_encounter_results(location_name, pokemon_encounters, game_filter)
                
            else:
                # This is a regular location, get detailed location data
                location_data = self.get_location_details(location_info['url'])
                if not location_data:
                    print("❌ Could not load location details")
                    return
                
                # Extract Pokemon encounters
                pokemon_encounters = self.extract_pokemon_encounters(location_data, game_filter)
                
                if not pokemon_encounters:
                    if game_filter:
                        print(f"❌ No Pokemon encounters found for {location_name.replace('-', ' ').title()} in {game_filter.title()}")
                    else:
                        print(f"❌ No Pokemon encounters found for {location_name.replace('-', ' ').title()}")
                    return
                
                # Display the results
                self.display_encounter_results(location_name, pokemon_encounters, game_filter)
            
        except Exception as e:
            print(f"❌ Error displaying location Pokemon: {e}")
    
    def extract_area_encounters(self, area_data: Dict[str, Any], game_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract Pokemon encounter information from a single area"""
        encounters = []
        
        area_encounters = area_data.get('pokemon_encounters', [])
        print(f"DEBUG: Found {len(area_encounters)} pokemon encounters in this area")
        
        for encounter in area_encounters:
            pokemon_name = encounter['pokemon']['name']
            version_details = encounter.get('version_details', [])
            
            print(f"DEBUG: Processing {pokemon_name} with {len(version_details)} version details")
            
            # Filter by game if specified
            if game_filter:
                filtered_details = []
                for vd in version_details:
                    version_name = vd['version']['name']
                    if version_name == game_filter.lower():
                        filtered_details.append(vd)
                        print(f"DEBUG: Found match for {pokemon_name} in {version_name}")
                version_details = filtered_details
            
            if version_details:
                encounter_info = {
                    'pokemon_name': pokemon_name,
                    'area_name': area_data.get('name', 'Unknown Area'),
                    'version_details': version_details
                }
                encounters.append(encounter_info)
            else:
                if game_filter:
                    print(f"DEBUG: {pokemon_name} not found in {game_filter}")
        
        print(f"DEBUG: Returning {len(encounters)} encounters after filtering")
        return encounters
    
    def get_location_details(self, location_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific location"""
        try:
            if location_url in self.location_cache:
                return self.location_cache[location_url]
            
            response = requests.get(location_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.location_cache[location_url] = data
                return data
            else:
                return None
                
        except Exception as e:
            print(f"Error loading location details: {e}")
            return None
    
    def extract_pokemon_encounters(self, location_data: Dict[str, Any], game_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract Pokemon encounter information from location data"""
        encounters = []
        
        # Get all areas within this location
        areas = location_data.get('areas', [])
        
        for area in areas:
            area_data = self.get_area_details(area['url'])
            if not area_data:
                continue
            
            area_encounters = area_data.get('pokemon_encounters', [])
            
            for encounter in area_encounters:
                pokemon_name = encounter['pokemon']['name']
                version_details = encounter.get('version_details', [])
                
                # Filter by game if specified
                if game_filter:
                    version_details = [vd for vd in version_details if vd['version']['name'] == game_filter.lower()]
                
                if version_details:
                    encounter_info = {
                        'pokemon_name': pokemon_name,
                        'area_name': area_data.get('name', 'Unknown Area'),
                        'version_details': version_details
                    }
                    encounters.append(encounter_info)
        
        return encounters
    
    def get_area_details(self, area_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific area"""
        try:
            if area_url in self.location_cache:
                return self.location_cache[area_url]
            
            response = requests.get(area_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.location_cache[area_url] = data
                return data
            else:
                return None
                
        except Exception as e:
            print(f"Error loading area details: {e}")
            return None
    
    def display_encounter_results(self, location_name: str, encounters: List[Dict[str, Any]], game_filter: Optional[str] = None) -> None:
        """Display the Pokemon encounter results in a compact, multi-column format with full information"""
        try:
            display_name = location_name.replace('-', ' ').title()
            
            # Create header
            if game_filter:
                header = f"{display_name} - Pokemon Encounters ({game_filter.title()})"
            else:
                header = f"{display_name} - Pokemon Encounters"
            
            print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║{header:^115}║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣""")
            
            # Group encounters by Pokemon
            pokemon_dict = {}
            for encounter in encounters:
                pokemon_name = encounter['pokemon_name']
                if pokemon_name not in pokemon_dict:
                    pokemon_dict[pokemon_name] = {
                        'areas': set(),
                        'encounter_details': []
                    }
                
                pokemon_dict[pokemon_name]['areas'].add(encounter['area_name'])
                pokemon_dict[pokemon_name]['encounter_details'].extend(encounter['version_details'])
            
            if not pokemon_dict:
                print("║                                           No Pokemon found                                                ║")
                print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
                return
            
            # Convert to list with full encounter info
            pokemon_list = []
            for pokemon_name in sorted(pokemon_dict.keys()):
                pokemon_info = pokemon_dict[pokemon_name]
                
                # Get all encounter methods (not just the best one)
                encounter_methods = self._get_all_encounter_methods(pokemon_info['encounter_details'])
                areas_text = ", ".join(sorted(pokemon_info['areas'])).replace('-', ' ').title()
                
                pokemon_list.append({
                    'name': pokemon_name.replace('-', ' ').title(),
                    'areas': areas_text,
                    'methods': encounter_methods
                })
            
            # Display Pokemon in rows of 2 for better readability
            self._display_pokemon_two_column(pokemon_list)
            
            print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            print(f"Error displaying encounter results: {e}")
    
    def _get_all_encounter_methods(self, encounter_details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get all encounter methods for a Pokemon with full details"""
        try:
            methods = {}
            
            for detail in encounter_details:
                for encounter_detail in detail.get('encounter_details', []):
                    method_name = encounter_detail.get('method', {}).get('name', 'walk')
                    chance = encounter_detail.get('chance', 0)
                    max_level = encounter_detail.get('max_level', '?')
                    min_level = encounter_detail.get('min_level', '?')
                    
                    method_key = f"{method_name}_{min_level}_{max_level}"
                    
                    if method_key not in methods:
                        methods[method_key] = {
                            'method': method_name.replace('-', ' ').title(),
                            'chance': chance,
                            'levels': f"{min_level}-{max_level}" if min_level != '?' and max_level != '?' else '?',
                            'min_level': min_level,
                            'max_level': max_level
                        }
                    else:
                        # Keep the higher chance if duplicate
                        if chance > methods[method_key]['chance']:
                            methods[method_key]['chance'] = chance
            
            # Sort by chance (highest first)
            return sorted(methods.values(), key=lambda x: x['chance'], reverse=True)
            
        except Exception:
            return [{'method': 'Unknown', 'chance': 0, 'levels': '?'}]
    
    def _display_pokemon_two_column(self, pokemon_list: List[Dict[str, Any]]) -> None:
        """Display Pokemon in a two-column format with proper alignment"""
        try:
            # Define column width - make it slightly smaller for better alignment
            col_width = 50
            
            print("║                                                                                                                 ║")
            
            # Process Pokemon in groups of 2
            for i in range(0, len(pokemon_list), 2):
                batch = pokemon_list[i:i+2]
                
                # Format first Pokemon (left column)
                pokemon1 = batch[0]
                col1_lines = []
                
                # Pokemon name
                col1_lines.append(f"{pokemon1['name']}")
                
                # Areas line
                areas1 = pokemon1['areas']
                if len(areas1) > col_width - 8:  # Account for "Areas: " prefix
                    areas1 = areas1[:col_width - 11] + "..."
                col1_lines.append(f"Areas: {areas1}")
                
                # Encounter methods
                for method in pokemon1['methods']:
                    method_line = f"{method['method']}: {method['chance']}%, Lv.{method['levels']}"
                    # Truncate if too long for column
                    if len(method_line) > col_width - 2:
                        method_line = f"{method['method']}: {method['chance']}%"
                        if len(method_line) > col_width - 2:
                            method_line = method_line[:col_width - 5] + "..."
                    col1_lines.append(method_line)
                
                # Format second Pokemon (right column) if it exists
                col2_lines = []
                if len(batch) > 1:
                    pokemon2 = batch[1]
                    
                    # Pokemon name
                    col2_lines.append(f"{pokemon2['name']}")
                    
                    # Areas line
                    areas2 = pokemon2['areas']
                    if len(areas2) > col_width - 8:  # Account for "Areas: " prefix
                        areas2 = areas2[:col_width - 11] + "..."
                    col2_lines.append(f"Areas: {areas2}")
                    
                    # Encounter methods
                    for method in pokemon2['methods']:
                        method_line = f"{method['method']}: {method['chance']}%, Lv.{method['levels']}"
                        # Truncate if too long for column
                        if len(method_line) > col_width - 2:
                            method_line = f"{method['method']}: {method['chance']}%"
                            if len(method_line) > col_width - 2:
                                method_line = method_line[:col_width - 5] + "..."
                        col2_lines.append(method_line)
                
                # Make both columns the same height
                max_lines = max(len(col1_lines), len(col2_lines))
                while len(col1_lines) < max_lines:
                    col1_lines.append("")
                while len(col2_lines) < max_lines:
                    col2_lines.append("")
                
                # Print all lines for this Pokemon pair with proper alignment
                for j in range(max_lines):
                    line1 = col1_lines[j][:col_width]  # Ensure exact width
                    line2 = col2_lines[j][:col_width] if j < len(col2_lines) else ""
                    
                    # Left-align within each column, then space columns apart
                    formatted_line = f"{line1:<{col_width}}   {line2:<{col_width}}"
                    
                    # Trim trailing spaces and center the whole thing
                    formatted_line = formatted_line.rstrip()
                    padded_line = f" {formatted_line:<111} "
                    print(f"║{padded_line}║")
                
                # Add spacing between Pokemon pairs (except last)
                if i + 2 < len(pokemon_list):
                    print("║                                                                                                                 ║")
            
            print("║                                                                                                                 ║")
            
        except Exception as e:
            print(f"Error displaying Pokemon two-column: {e}")
            # Fallback to simple single-column list
            for pokemon in pokemon_list:
                name_line = f" {pokemon['name']:<111} "
                print(f"║{name_line}║")
                
                areas_line = f" Areas: {pokemon['areas'][:100]:<104} "
                print(f"║{areas_line}║")
                
                for method in pokemon['methods']:
                    method_line = f" {method['method']}: {method['chance']}%, Lv.{method['levels']}"
                    method_padded = f" {method_line:<111} "
                    print(f"║{method_padded}║")
                    
                print("║                                                                                                                 ║")