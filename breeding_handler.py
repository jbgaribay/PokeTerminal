# breeding_handler.py
"""
Pokemon breeding compatibility and analysis for the Pokédex Terminal App
"""

import requests
from typing import Dict, Any, List, Optional, Tuple
from api_client import PokeAPIClient
from display_utils import DisplayFormatter

class BreedingHandler:
    """Handles Pokemon breeding compatibility analysis and egg move calculations"""
    
    def __init__(self):
        self.api_client = PokeAPIClient()
        self.formatter = DisplayFormatter()
        self.egg_group_cache = {}
    
    def handle_breeding_command(self, query: str) -> None:
        """Handle breeding compatibility command: 'breed pokemon1 pokemon2'"""
        try:
            # Parse breed command: "breed pikachu ditto"
            parts = query.split()
            if len(parts) != 3:
                print("❌ Invalid breeding format! Use: breed <pokemon1> <pokemon2>")
                print("   Example: breed pikachu ditto")
                return
            
            pokemon1_name = parts[1].lower()
            pokemon2_name = parts[2].lower()
            
            print(f"\n🔍 Analyzing breeding compatibility between {pokemon1_name.title()} and {pokemon2_name.title()}...")
            
            # Get Pokemon data
            pokemon1_data = self.api_client.get_pokemon_data(pokemon1_name)
            pokemon2_data = self.api_client.get_pokemon_data(pokemon2_name)
            
            if not pokemon1_data:
                print(f"❌ Could not find Pokémon: {pokemon1_name}")
                return
            
            if not pokemon2_data:
                print(f"❌ Could not find Pokémon: {pokemon2_name}")
                return
            
            # Perform breeding analysis
            self.analyze_breeding_compatibility(pokemon1_data, pokemon2_data)
            
        except Exception as e:
            print(f"❌ Error analyzing breeding compatibility: {e}")
    
    def analyze_breeding_compatibility(self, pokemon1_data: Dict[str, Any], pokemon2_data: Dict[str, Any]) -> None:
        """Analyze and display breeding compatibility between two Pokemon"""
        try:
            pokemon1 = pokemon1_data['pokemon']
            pokemon2 = pokemon2_data['pokemon']
            species1 = pokemon1_data['species']
            species2 = pokemon2_data['species']
            
            name1 = pokemon1['name'].title()
            name2 = pokemon2['name'].title()
            
            # Check basic compatibility
            compatibility_result = self.check_breeding_compatibility(species1, species2, pokemon1, pokemon2)
            
            # Get egg groups
            egg_groups1 = self.get_pokemon_egg_groups(species1)
            egg_groups2 = self.get_pokemon_egg_groups(species2)
            
            # Determine offspring species (always female parent or non-Ditto parent)
            offspring_info = self.determine_offspring(species1, species2, name1, name2)
            
            # Get possible egg moves
            possible_egg_moves = self.get_possible_egg_moves(pokemon1_data, pokemon2_data, offspring_info)
            
            # Display the full analysis
            self.display_breeding_analysis(
                name1, name2, compatibility_result, egg_groups1, egg_groups2, 
                offspring_info, possible_egg_moves
            )
            
        except Exception as e:
            print(f"Error in breeding analysis: {e}")
    
    def check_breeding_compatibility(self, species1: Dict[str, Any], species2: Dict[str, Any], 
                                   pokemon1: Dict[str, Any], pokemon2: Dict[str, Any]) -> Dict[str, Any]:
        """Check if two Pokemon can breed together"""
        try:
            # Get basic info
            name1 = species1.get('name', '').title()
            name2 = species2.get('name', '').title()
            
            # Get egg groups
            egg_groups1 = self.get_pokemon_egg_groups(species1)
            egg_groups2 = self.get_pokemon_egg_groups(species2)
            
            # Check for No Eggs Discovered group
            if 'no-eggs-discovered' in egg_groups1 or 'no-eggs-discovered' in egg_groups2:
                return {
                    'compatible': False,
                    'reason': 'One or both Pokemon cannot breed (No Eggs Discovered group)',
                    'shared_groups': []
                }
            
            # Special case: Ditto can breed with almost anyone
            if 'ditto' in egg_groups1 or 'ditto' in egg_groups2:
                if 'ditto' in egg_groups1 and 'ditto' in egg_groups2:
                    return {
                        'compatible': False,
                        'reason': 'Ditto cannot breed with another Ditto',
                        'shared_groups': []
                    }
                return {
                    'compatible': True,
                    'reason': 'Ditto can breed with any breedable Pokemon',
                    'shared_groups': ['ditto']
                }
            
            # Check for shared egg groups
            shared_groups = list(set(egg_groups1) & set(egg_groups2))
            
            if not shared_groups:
                return {
                    'compatible': False,
                    'reason': 'No shared egg groups',
                    'shared_groups': []
                }
            
            # Check gender compatibility (simplified - would need gender data for full implementation)
            # For now, assume compatibility if they share egg groups
            return {
                'compatible': True,
                'reason': 'Shared egg groups',
                'shared_groups': shared_groups
            }
            
        except Exception as e:
            print(f"Error checking compatibility: {e}")
            return {
                'compatible': False,
                'reason': 'Error in compatibility check',
                'shared_groups': []
            }
    
    def get_pokemon_egg_groups(self, species_data: Dict[str, Any]) -> List[str]:
        """Get egg groups for a Pokemon species"""
        try:
            egg_groups = []
            for group in species_data.get('egg_groups', []):
                group_name = group.get('name', '')
                if group_name:
                    egg_groups.append(group_name)
            return egg_groups
        except Exception:
            return []
    
    def determine_offspring(self, species1: Dict[str, Any], species2: Dict[str, Any], 
                          name1: str, name2: str) -> Dict[str, Any]:
        """Determine what the offspring would be"""
        try:
            # Get egg groups to check for Ditto
            egg_groups1 = self.get_pokemon_egg_groups(species1)
            egg_groups2 = self.get_pokemon_egg_groups(species2)
            
            # If one is Ditto, offspring is the non-Ditto parent
            if 'ditto' in egg_groups1:
                return {
                    'species': name2,
                    'parent_species': species2,
                    'rule': 'Ditto breeding - offspring is non-Ditto parent'
                }
            elif 'ditto' in egg_groups2:
                return {
                    'species': name1,
                    'parent_species': species1,
                    'rule': 'Ditto breeding - offspring is non-Ditto parent'
                }
            
            # In normal breeding, offspring is typically the female parent
            # For simplicity, we'll say it could be either (would need gender data for accuracy)
            return {
                'species': f"{name1} or {name2}",
                'parent_species': species1,  # Default to first
                'rule': 'Offspring species depends on female parent'
            }
            
        except Exception:
            return {
                'species': 'Unknown',
                'parent_species': None,
                'rule': 'Unable to determine offspring'
            }
    
    def get_possible_egg_moves(self, pokemon1_data: Dict[str, Any], pokemon2_data: Dict[str, Any], 
                             offspring_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get possible egg moves that could be inherited"""
        try:
            possible_moves = []
            
            # Determine which Pokemon would be the child and which would be the father
            offspring_species = offspring_info.get('parent_species')
            if not offspring_species:
                return []
            
            # Get the offspring Pokemon data to find its egg moves
            offspring_name = offspring_species.get('name', '')
            if not offspring_name:
                return []
            
            # Get egg moves for the offspring species
            offspring_pokemon_data = self.api_client.get_pokemon_data(offspring_name)
            if not offspring_pokemon_data:
                return possible_moves
            
            # Extract egg moves from the offspring's moveset
            offspring_egg_moves = []
            for move_entry in offspring_pokemon_data['pokemon'].get('moves', []):
                for version_detail in move_entry.get('version_group_details', []):
                    if version_detail['move_learn_method']['name'] == 'egg':
                        move_name = move_entry['move']['name'].replace('-', ' ').title()
                        if move_name not in [m['name'] for m in offspring_egg_moves]:
                            offspring_egg_moves.append({
                                'name': move_name,
                                'learned_by': 'egg'
                            })
                        break
            
            if not offspring_egg_moves:
                return [{
                    'name': 'No egg moves available',
                    'source': 'None',
                    'description': f'{offspring_name.title()} cannot learn moves through breeding'
                }]
            
            # Check which of these egg moves the parents can learn
            parent1_moves = self.get_pokemon_learnable_moves(pokemon1_data['pokemon'])
            parent2_moves = self.get_pokemon_learnable_moves(pokemon2_data['pokemon'])
            
            for egg_move in offspring_egg_moves[:10]:  # Limit to 10 for display
                move_name = egg_move['name']
                sources = []
                
                if move_name.lower().replace(' ', '-') in parent1_moves:
                    sources.append(pokemon1_data['pokemon']['name'].title())
                if move_name.lower().replace(' ', '-') in parent2_moves:
                    sources.append(pokemon2_data['pokemon']['name'].title())
                
                if sources:
                    possible_moves.append({
                        'name': move_name,
                        'source': ' or '.join(sources),
                        'description': f'Can be inherited if parent knows this move'
                    })
                else:
                    possible_moves.append({
                        'name': move_name,
                        'source': 'Chain breeding required',
                        'description': 'Neither parent can learn this move directly'
                    })
            
            return possible_moves if possible_moves else [{
                'name': 'Analysis incomplete',
                'source': 'API limitation',
                'description': 'Unable to determine egg move compatibility'
            }]
            
        except Exception as e:
            print(f"Error getting egg moves: {e}")
            return [{
                'name': 'Error in analysis',
                'source': 'System error',
                'description': 'Could not analyze egg move possibilities'
            }]
    
    def get_pokemon_learnable_moves(self, pokemon_data: Dict[str, Any]) -> List[str]:
        """Get all moves a Pokemon can learn by any method"""
        try:
            learnable_moves = []
            
            for move_entry in pokemon_data.get('moves', []):
                move_name = move_entry['move']['name']
                learnable_moves.append(move_name)
            
            return learnable_moves
            
        except Exception:
            return []
    
    def get_egg_group_pokemon(self, egg_group_name: str) -> List[str]:
        """Get all Pokemon in a specific egg group"""
        try:
            if egg_group_name in self.egg_group_cache:
                return self.egg_group_cache[egg_group_name]
            
            # Fetch egg group data from API
            response = requests.get(f"https://pokeapi.co/api/v2/egg-group/{egg_group_name}")
            if response.status_code != 200:
                return []
            
            data = response.json()
            pokemon_list = []
            
            for species in data.get('pokemon_species', []):
                pokemon_name = species.get('name', '').replace('-', ' ').title()
                if pokemon_name:
                    pokemon_list.append(pokemon_name)
            
            # Cache the result
            self.egg_group_cache[egg_group_name] = pokemon_list
            return pokemon_list
            
        except Exception as e:
            print(f"Error fetching egg group data: {e}")
            return []
    
    def display_breeding_analysis(self, name1: str, name2: str, compatibility: Dict[str, Any], 
                                egg_groups1: List[str], egg_groups2: List[str], 
                                offspring_info: Dict[str, Any], egg_moves: List[Dict[str, Any]]) -> None:
        """Display the complete breeding analysis"""
        try:
            # Create header
            header = f"{name1} × {name2} BREEDING ANALYSIS"
            
            print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║{header:^115}║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣""")
            
            # Compatibility status
            if compatibility['compatible']:
                status_line = "COMPATIBILITY: ✅ Compatible"
                reason_line = f"REASON: {compatibility['reason']}"
            else:
                status_line = "COMPATIBILITY: ❌ Not Compatible"
                reason_line = f"REASON: {compatibility['reason']}"
            
            print(f"║ {status_line:<111} ║")
            print(f"║ {reason_line:<111} ║")
            print("║                                                                                                                 ║")
            
            # Egg groups information
            if compatibility['compatible']:
                # Shared egg groups
                if compatibility['shared_groups']:
                    shared_text = ", ".join([group.replace('-', ' ').title() for group in compatibility['shared_groups']])
                    shared_line = f"SHARED EGG GROUPS: {shared_text}"
                    print(f"║ {shared_line:<111} ║")
                
                # Individual egg groups
                groups1_text = ", ".join([group.replace('-', ' ').title() for group in egg_groups1])
                groups2_text = ", ".join([group.replace('-', ' ').title() for group in egg_groups2])
                
                groups1_line = f"{name1} EGG GROUPS: {groups1_text}"
                groups2_line = f"{name2} EGG GROUPS: {groups2_text}"
                
                print(f"║ {groups1_line:<111} ║")
                print(f"║ {groups2_line:<111} ║")
                print("║                                                                                                                 ║")
                
                # Offspring information
                offspring_line = f"OFFSPRING: {offspring_info.get('species', 'Unknown')}"
                rule_line = f"RULE: {offspring_info.get('rule', 'Standard breeding rules apply')}"
                
                print(f"║ {offspring_line:<111} ║")
                print(f"║ {rule_line:<111} ║")
                print("║                                                                                                                 ║")
                
                # Egg moves analysis
                if egg_moves and len(egg_moves) > 0:
                    print("║ POSSIBLE EGG MOVES:                                                                                         ║")
                    
                    for move in egg_moves[:8]:  # Show first 8 egg moves
                        move_name = move.get('name', 'Unknown')
                        move_source = move.get('source', 'Unknown')
                        
                        # Format the move line
                        if len(move_name) > 25:
                            move_name = move_name[:22] + "..."
                        if len(move_source) > 40:
                            move_source = move_source[:37] + "..."
                        
                        move_line = f"• {move_name:<25} (from: {move_source})"
                        print(f"║ {move_line:<111} ║")
                    
                    if len(egg_moves) > 8:
                        more_line = f"... and {len(egg_moves) - 8} more potential egg moves"
                        print(f"║ {more_line:<111} ║")
                    
                    print("║                                                                                                                 ║")
                
                # Egg group connections (show some Pokemon from shared groups)
                if compatibility['shared_groups']:
                    print("║ EGG GROUP CONNECTIONS:                                                                                      ║")
                    
                    for group in compatibility['shared_groups'][:2]:  # Show first 2 shared groups
                        group_pokemon = self.get_egg_group_pokemon(group)
                        if group_pokemon:
                            # Show first few Pokemon in this group
                            sample_pokemon = ", ".join(group_pokemon[:8])  # First 8 Pokemon
                            if len(group_pokemon) > 8:
                                sample_pokemon += f"... (+{len(group_pokemon) - 8} more)"
                            
                            group_title = group.replace('-', ' ').title()
                            group_line = f"{group_title} Group: {sample_pokemon}"
                            
                            # Handle long lines by wrapping
                            if len(group_line) > 111:
                                # Split into multiple lines
                                words = group_line.split()
                                current_line = ""
                                
                                for word in words:
                                    if len(current_line + " " + word) <= 111:
                                        if current_line:
                                            current_line += " " + word
                                        else:
                                            current_line = word
                                    else:
                                        if current_line:
                                            print(f"║ {current_line:<111} ║")
                                            current_line = word
                                        else:
                                            # Word too long, truncate
                                            print(f"║ {word[:111]:<111} ║")
                                            current_line = ""
                                
                                if current_line:
                                    print(f"║ {current_line:<111} ║")
                            else:
                                print(f"║ {group_line:<111} ║")
                    
                    print("║                                                                                                                 ║")
                
                # Breeding tips
                print("║ BREEDING TIPS:                                                                                             ║")
                print("║ • Egg moves are inhereted from Father pokemon (Gen 1 - Gen 5)                                              ║")
                print("║ • Egg moves are inherited from either parent (Gen 6+)                                                      ║")
                print("║ • Use 'moves gen X egg' command to see specific egg moves                                                  ║")
                print("║ • Ditto can breed with any non-legendary, breedable Pokemon                                                ║")
                print("║ • Offspring will be the lowest evolution of the female parent's line                                       ║")
                
            
            else:
                # Show why they can't breed and suggestions
                print("║ BREEDING SUGGESTIONS:                                                                                       ║")
                
                # Show egg groups for reference
                if egg_groups1:
                    groups1_text = ", ".join([group.replace('-', ' ').title() for group in egg_groups1])
                    groups1_line = f"{name1} is in: {groups1_text}"
                    print(f"║ {groups1_line:<111} ║")
                
                if egg_groups2:
                    groups2_text = ", ".join([group.replace('-', ' ').title() for group in egg_groups2])
                    groups2_line = f"{name2} is in: {groups2_text}"
                    print(f"║ {groups2_line:<111} ║")
                
                print("║                                                                                                                 ║")
                print("║ Try using Ditto, or find Pokemon that share egg groups!                                                    ║")
            
            print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            print(f"Error displaying breeding analysis: {e}")
    
    def get_breeding_suggestions(self, pokemon_data: Dict[str, Any]) -> List[str]:
        """Get breeding suggestions for a Pokemon"""
        try:
            species = pokemon_data['species']
            egg_groups = self.get_pokemon_egg_groups(species)
            
            suggestions = []
            
            # Always suggest Ditto first
            if 'no-eggs-discovered' not in egg_groups:
                suggestions.append("Ditto (universal breeding partner)")
            
            # Get some Pokemon from each egg group
            for group in egg_groups[:2]:  # Limit to first 2 groups
                group_pokemon = self.get_egg_group_pokemon(group)
                if group_pokemon:
                    # Suggest a few popular choices
                    popular_choices = [p for p in group_pokemon[:5] if p.lower() != pokemon_data['pokemon']['name']]
                    if popular_choices:
                        suggestions.extend(popular_choices[:3])
            
            return suggestions[:10]  # Return top 10 suggestions
            
        except Exception:
            return ["Ditto"]