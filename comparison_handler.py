# comparison_handler.py
"""
Pokemon comparison handling and display for the Pokédx Terminal App
"""

from typing import Dict, Any, List, Optional, Tuple
from api_client import PokeAPIClient
from display_utils import DisplayFormatter

class ComparisonHandler:
    """Handles Pokemon-to-Pokemon comparison with side-by-side display"""
    
    def __init__(self):
        self.api_client = PokeAPIClient()
        self.formatter = DisplayFormatter()
    
    def compare_pokemon(self, pokemon1_name: str, pokemon2_name: str) -> None:
        """Compare two Pokemon side by side"""
        try:
            print(f"\n🔍 Loading {pokemon1_name.title()} and {pokemon2_name.title()} for comparison...")
            
            # Get data for both Pokemon
            pokemon1_data = self.api_client.get_pokemon_data(pokemon1_name)
            pokemon2_data = self.api_client.get_pokemon_data(pokemon2_name)
            
            if not pokemon1_data:
                print(f"❌ Could not find Pokémon: {pokemon1_name}")
                return
            
            if not pokemon2_data:
                print(f"❌ Could not find Pokémon: {pokemon2_name}")
                return
            
            # Display the comparison
            self.display_comparison(pokemon1_data['pokemon'], pokemon2_data['pokemon'])
            
        except Exception as e:
            print(f"❌ Error comparing Pokémon: {e}")
    
    def display_comparison(self, pokemon1: Dict[str, Any], pokemon2: Dict[str, Any]) -> None:
        """Display two Pokemon side by side with stats comparison"""
        try:
            name1 = pokemon1['name'].title()
            name2 = pokemon2['name'].title()
            
            print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                        {name1} VS {name2} - COMPARISON                                        ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣""")
            
            # Generate sprites for both Pokemon
            sprite1_lines = self._get_pokemon_sprite(pokemon1, width=50)
            sprite2_lines = self._get_pokemon_sprite(pokemon2, width=50)
            
            # Display sprites side by side
            self._display_sprites_side_by_side(sprite1_lines, sprite2_lines, name1, name2)
            
            # Display basic info comparison
            self._display_basic_info_comparison(pokemon1, pokemon2)
            
            # Display stats comparison
            self._display_stats_comparison(pokemon1, pokemon2)
            
            # Display types comparison
            self._display_types_comparison(pokemon1, pokemon2)
            
            # Display abilities comparison
            self._display_abilities_comparison(pokemon1, pokemon2)
            
            print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            print(f"Error displaying comparison: {e}")
    
    def _get_pokemon_sprite(self, pokemon: Dict[str, Any], width: int) -> List[str]:
        """Get ASCII sprite for a Pokemon"""
        try:
            sprite_url = pokemon.get('sprites', {}).get('front_default')
            if sprite_url:
                sprite_ascii = self.formatter.get_sprite_ascii(sprite_url, width=width)
                return sprite_ascii.split('\n')
            else:
                return ["No sprite available"] + [""] * 20
        except Exception:
            return ["Sprite error"] + [""] * 20
    
    def _display_sprites_side_by_side(self, sprite1_lines: List[str], sprite2_lines: List[str], 
                                    name1: str, name2: str) -> None:
        """Display two sprites side by side"""
        try:
            # Ensure both sprites have the same height
            max_height = max(len(sprite1_lines), len(sprite2_lines), 25)
            sprite1_lines = (sprite1_lines + [''] * max_height)[:max_height]
            sprite2_lines = (sprite2_lines + [''] * max_height)[:max_height]
            
            # Format sprites to consistent width
            sprite_width = 50
            sprite1_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite1_lines]
            sprite2_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite2_lines]
            
            print("║                                                                                                                 ║")
            
            # Display names above sprites
            name_line = f"{name1:^50}   {name2:^50}"
            name_line = name_line.center(111)
            print(f"║ {name_line} ║")
            
            print("║                                                                                                                 ║")
            
            # Display sprites side by side
            for i in range(max_height):
                sprite1_part = sprite1_lines[i]
                sprite2_part = sprite2_lines[i]
                
                # Combine with VS in the middle
                if i == max_height // 2:
                    line = f"{sprite1_part} VS {sprite2_part}"
                else:
                    line = f"{sprite1_part}    {sprite2_part}"
                
                # Center the line
                line = line.center(111)
                print(f"║ {line} ║")
            
            print("║                                                                                                                 ║")
            
        except Exception as e:
            print(f"Error displaying sprites: {e}")
    
    def _display_basic_info_comparison(self, pokemon1: Dict[str, Any], pokemon2: Dict[str, Any]) -> None:
        """Display basic info comparison"""
        try:
            print("║                                           BASIC INFORMATION                                           ║")
            print("╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")
            
            # Get basic info
            height1 = pokemon1.get('height', 0) / 10  # Convert to meters
            height2 = pokemon2.get('height', 0) / 10
            weight1 = pokemon1.get('weight', 0) / 10  # Convert to kg
            weight2 = pokemon2.get('weight', 0) / 10
            id1 = pokemon1.get('id', 0)
            id2 = pokemon2.get('id', 0)
            
            # Display comparisons
            comparison_lines = [
                f"Pokédex ID:      #{id1:<8}                        #{id2:<8}",
                f"Height:          {height1:<8.1f}m                     {height2:<8.1f}m",
                f"Weight:          {weight1:<8.1f}kg                     {weight2:<8.1f}kg"
            ]
            
            for line in comparison_lines:
                padded_line = line.center(111)
                print(f"║ {padded_line} ║")
            
            print("║                                                                                                                 ║")
            
        except Exception as e:
            print(f"Error displaying basic info: {e}")
    
    def _display_stats_comparison(self, pokemon1: Dict[str, Any], pokemon2: Dict[str, Any]) -> None:
        """Display stats comparison with visual bars"""
        try:
            print("║                                             BASE STATS                                               ║")
            print("╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")
            
            # Get stats for both Pokemon
            stats1 = {stat['stat']['name']: stat['base_stat'] for stat in pokemon1.get('stats', [])}
            stats2 = {stat['stat']['name']: stat['base_stat'] for stat in pokemon2.get('stats', [])}
            
            # Define stat order and display names
            stat_order = [
                ('hp', 'HP'),
                ('attack', 'Attack'),
                ('defense', 'Defense'),
                ('special-attack', 'Sp. Atk'),
                ('special-defense', 'Sp. Def'),
                ('speed', 'Speed')
            ]
            
            for stat_key, stat_name in stat_order:
                value1 = stats1.get(stat_key, 0)
                value2 = stats2.get(stat_key, 0)
                
                # Create visual comparison
                self._display_stat_comparison_line(stat_name, value1, value2)
            
            # Calculate and display totals
            total1 = sum(stats1.values())
            total2 = sum(stats2.values())
            
            print("║                                                                                                                 ║")
            self._display_stat_comparison_line("TOTAL", total1, total2, is_total=True)
            print("║                                                                                                                 ║")
            
        except Exception as e:
            print(f"Error displaying stats: {e}")
    
    def _display_stat_comparison_line(self, stat_name: str, value1: int, value2: int, is_total: bool = False) -> None:
        """Display a single stat comparison line with visual bars"""
        try:
            # Determine winner
            if value1 > value2:
                winner1, winner2 = "►", " "
            elif value2 > value1:
                winner1, winner2 = " ", "◄"
            else:
                winner1, winner2 = "=", "="
            
            # Create visual bars (scale to max 20 characters)
            max_value = max(value1, value2, 1)
            bar_length = 20
            
            bar1_len = int((value1 / max_value) * bar_length)
            bar2_len = int((value2 / max_value) * bar_length)
            
            bar1 = "█" * bar1_len + "░" * (bar_length - bar1_len)
            bar2 = "█" * bar2_len + "░" * (bar_length - bar2_len)
            
            # Format the line
            if is_total:
                line = f"{stat_name:>8}: {winner1} {value1:>3} [{bar1}] VS [{bar2}] {value2:<3} {winner2}"
            else:
                line = f"{stat_name:>8}: {winner1} {value1:>3} [{bar1}] VS [{bar2}] {value2:<3} {winner2}"
            
            padded_line = line.center(111)
            print(f"║ {padded_line} ║")
            
        except Exception as e:
            print(f"Error displaying stat line: {e}")
    
    def _display_types_comparison(self, pokemon1: Dict[str, Any], pokemon2: Dict[str, Any]) -> None:
        """Display types comparison"""
        try:
            print("║                                               TYPES                                                  ║")
            print("╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")
            
            # Get types
            types1 = [t['type']['name'].title() for t in pokemon1.get('types', [])]
            types2 = [t['type']['name'].title() for t in pokemon2.get('types', [])]
            
            # Format types
            types1_str = " / ".join(types1) if types1 else "No types"
            types2_str = " / ".join(types2) if types2 else "No types"
            
            # Display types comparison
            types_line = f"{types1_str:^45}     VS     {types2_str:^45}"
            types_line = types_line.center(111)
            print(f"║ {types_line} ║")
            
            print("║                                                                                                                 ║")
            
        except Exception as e:
            print(f"Error displaying types: {e}")
    
    def _display_abilities_comparison(self, pokemon1: Dict[str, Any], pokemon2: Dict[str, Any]) -> None:
        """Display abilities comparison"""
        try:
            print("║                                             ABILITIES                                               ║")
            print("╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣")
            
            # Get abilities
            abilities1 = []
            abilities2 = []
            
            for ability in pokemon1.get('abilities', []):
                ability_name = ability['ability']['name'].replace('-', ' ').title()
                if ability.get('is_hidden'):
                    ability_name += " (Hidden)"
                abilities1.append(ability_name)
            
            for ability in pokemon2.get('abilities', []):
                ability_name = ability['ability']['name'].replace('-', ' ').title()
                if ability.get('is_hidden'):
                    ability_name += " (Hidden)"
                abilities2.append(ability_name)
            
            # Display abilities
            max_abilities = max(len(abilities1), len(abilities2), 1)
            
            for i in range(max_abilities):
                ability1 = abilities1[i] if i < len(abilities1) else ""
                ability2 = abilities2[i] if i < len(abilities2) else ""
                
                abilities_line = f"{ability1:^45}     VS     {ability2:^45}"
                abilities_line = abilities_line.center(111)
                print(f"║ {abilities_line} ║")
            
            print("║                                                                                                                 ║")
            
        except Exception as e:
            print(f"Error displaying abilities: {e}")