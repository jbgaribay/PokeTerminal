# location_handler.py
"""
Location data handling and display for the Pokédex Terminal App
"""

from typing import Dict, Any, List
from api_client import PokeAPIClient
from display_utils import DisplayFormatter
from config import GEN_VERSION_GROUPS, VERSION_GROUP_MAP

class LocationHandler:
    """Handles location data fetching and display"""
    
    def __init__(self):
        self.api_client = PokeAPIClient()
        self.formatter = DisplayFormatter()
    
    def handle_location_query(self, query: str, pokemon_data: Dict[str, Any]) -> None:
        """Handle location query parsing and execution"""
        try:
            # Parse the query to extract generation and optional game
            # Expected formats: 
            # "location gen 3", "location gen 3 emerald"
            # Also handle: "location emerald", "location firered" (infer generation)
            
            parts = query.lower().split()
            
            if len(parts) < 2:
                print("❌ Invalid format! Use: location gen <number> [game] OR location <game>")
                print("   Examples: 'location gen 3', 'location gen 3 emerald', 'location emerald'")
                return
            
            generation = None
            specific_game = None
            
            if parts[1] == "gen":
                # Format: "location gen 3 [emerald]"
                if len(parts) < 3:
                    print("❌ Invalid format! Use: location gen <number> [game]")
                    return
                
                try:
                    generation = int(parts[2])
                    if generation < 1 or generation > 9:
                        print("❌ Generation must be between 1 and 9!")
                        return
                except ValueError:
                    print("❌ Invalid generation number!")
                    return
                
                # Extract optional game name
                if len(parts) > 3:
                    specific_game = "-".join(parts[3:])
            else:
                # Format: "location emerald" - infer generation from game
                specific_game = "-".join(parts[1:])
                generation = self._infer_generation_from_game(specific_game)
                
                if generation is None:
                    print(f"❌ Could not determine generation for game '{specific_game}'")
                    print("   Try using: location gen <number> <game>")
                    return
            
            print(f"\n🔍 Loading location data for {pokemon_data['name'].title()} (Generation {generation}" + 
                  (f", {specific_game.title()}" if specific_game else "") + ")...")
            
            # Get location data
            location_data = self.get_location_data(pokemon_data, generation, specific_game)
            
            if not location_data:
                print("❌ Could not load location data")
                return
            
            # Display the locations
            self.display_locations(pokemon_data['name'], generation, location_data)
            
        except Exception as e:
            print(f"❌ Error processing location query: {e}")
    
    def _infer_generation_from_game(self, game_name: str) -> int:
        """Infer generation number from game name"""
        game_to_generation = {
            'red': 1, 'blue': 1, 'yellow': 1,
            'gold': 2, 'silver': 2, 'crystal': 2,
            'ruby': 3, 'sapphire': 3, 'emerald': 3, 'firered': 3, 'leafgreen': 3,
            'diamond': 4, 'pearl': 4, 'platinum': 4, 'heartgold': 4, 'soulsilver': 4,
            'black': 5, 'white': 5, 'black-2': 5, 'white-2': 5,
            'x': 6, 'y': 6, 'omega-ruby': 6, 'alpha-sapphire': 6,
            'sun': 7, 'moon': 7, 'ultra-sun': 7, 'ultra-moon': 7,
            'sword': 8, 'shield': 8,
            'scarlet': 9, 'violet': 9
        }
        
        return game_to_generation.get(game_name.lower())
    
    def get_location_data(self, pokemon_data: Dict[str, Any], generation: int, specific_game: str = None) -> Dict[str, Any]:
        """Fetch location data for a specific generation and optionally a specific game"""
        try:
            # Get location area encounters
            encounters_data = self.api_client.get_location_encounters(pokemon_data)
            if encounters_data is None:
                return {
                    'locations': [],
                    'filter_info': {
                        'generation': generation,
                        'game': specific_game,
                        'display_name': specific_game.replace('-', ' ').title() if specific_game else f'Generation {generation}'
                    }
                }
            
            # Determine which version groups to include
            if specific_game and specific_game in GEN_VERSION_GROUPS.get(generation, {}):
                target_version_groups = GEN_VERSION_GROUPS[generation][specific_game]
                game_filter_text = specific_game.replace('-', ' ').title()
            else:
                target_version_groups = GEN_VERSION_GROUPS.get(generation, {}).get('all', [])
                game_filter_text = f"Generation {generation}"
            
            locations = []
            
            for encounter_area in encounters_data:
                location_area = encounter_area.get('location_area', {})
                area_name = location_area.get('name', 'Unknown Area')
                
                # Get the location name from the area
                area_url = location_area.get('url')
                location_name = 'Unknown Location'
                if area_url:
                    try:
                        area_data = self.api_client.get_location_area_details(area_url)
                        if area_data:
                            location_info = area_data.get('location', {})
                            if location_info and location_info.get('url'):
                                loc_data = self.api_client.get_location_details(location_info['url'])
                                if loc_data:
                                    location_name = loc_data.get('name', 'Unknown Location')
                    except:
                        pass
                
                # Process version details
                for version_detail in encounter_area.get('version_details', []):
                    version_name = version_detail.get('version', {}).get('name', '')
                    
                    # Map version to version group for filtering
                    version_group = VERSION_GROUP_MAP.get(version_name, version_name)
                    
                    # Check if this version group matches our target
                    if version_group not in target_version_groups:
                        continue
                    
                    # Process encounter details
                    for encounter_detail in version_detail.get('encounter_details', []):
                        method = encounter_detail.get('method', {}).get('name', 'Unknown')
                        min_level = encounter_detail.get('min_level', 0)
                        max_level = encounter_detail.get('max_level', 0)
                        chance = encounter_detail.get('chance', 0)
                        
                        # Format method name
                        method_formatted = method.replace('-', ' ').title()
                        
                        # Format level range
                        if min_level == max_level:
                            level_range = f"Lv. {min_level}"
                        else:
                            level_range = f"Lv. {min_level}-{max_level}"
                        
                        location_info = {
                            'location': location_name.replace('-', ' ').title(),
                            'area': area_name.replace('-', ' ').title(),
                            'method': method_formatted,
                            'level_range': level_range,
                            'chance': chance,
                            'version': version_name.title()
                        }
                        
                        locations.append(location_info)
            
            # Sort by location name, then by area
            locations.sort(key=lambda x: (x['location'], x['area']))
            
            # Remove duplicates while preserving order
            seen = set()
            unique_locations = []
            for loc in locations:
                loc_key = (loc['location'], loc['area'], loc['method'], loc['level_range'])
                if loc_key not in seen:
                    seen.add(loc_key)
                    unique_locations.append(loc)
            
            return {
                'locations': unique_locations,
                'filter_info': {
                    'generation': generation,
                    'game': specific_game,
                    'display_name': game_filter_text
                }
            }
            
        except Exception as e:
            print(f"Error fetching location data: {e}")
            return None
    
    def format_location_table(self, locations: list, title: str) -> str:
        """Format locations in a nice table"""
        if not locations:
            return f"{title}: None found"
        
        lines = [f"{title}:"]
        lines.append("─" * 80)
        
        # Add column headers
        header = f"{'LOCATION':<25} {'AREA':<20} {'METHOD':<15} {'LEVEL':<8} {'CHANCE':<6}"
        lines.append(header)
        lines.append("─" * 80)
        
        for location in locations[:25]:  # Limit to avoid overwhelming output
            loc_name = location['location'][:25].ljust(25)
            area_name = location['area'][:20].ljust(20)
            method = location['method'][:15].ljust(15)
            level_range = location['level_range'][:8].ljust(8)
            chance = f"{location['chance']}%".ljust(6)
            
            line = f"{loc_name} {area_name} {method} {level_range} {chance}"
            lines.append(line)
        
        if len(locations) > 25:
            lines.append(f"... and {len(locations) - 25} more locations")
        
        return '\n'.join(lines)

    def display_locations(self, pokemon_name: str, generation: int, location_data: Dict[str, Any]) -> None:
        """Display Pokemon location information in a formatted way"""
        try:
            # Get filter info for display
            filter_info = location_data.get('filter_info', {})
            display_name = filter_info.get('display_name', f'Generation {generation}')
            
            locations = location_data.get('locations', [])
            
            print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                       {pokemon_name.upper()} - {display_name.upper()} LOCATIONS                                       ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣""")
            
            if not locations:
                # No locations found message
                no_locations_msg = f"No encounter locations found for {display_name}"
                content_width = 113
                formatted_line = no_locations_msg[:content_width].ljust(content_width)
                print(f"║ {formatted_line} ║")
            else:
                # Format and display locations
                location_table = self.format_location_table(locations, "ENCOUNTER LOCATIONS")
                content_lines = location_table.split('\n')
                
                # Use formatter to handle bordered content
                formatted_lines = self.formatter.format_bordered_content(content_lines)
                for line in formatted_lines:
                    print(line)
            
            print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            print(f"Error displaying locations: {e}")