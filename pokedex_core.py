# pokedex_core.py
"""
Core Pokédex functionality for basic Pokemon information display
"""

import re
from typing import Dict, Any
from api_client import PokeAPIClient
from display_utils import DisplayFormatter

class PokedexCore:
    """Core Pokédex functionality for displaying basic Pokemon information"""
    
    def __init__(self):
        self.api_client = PokeAPIClient()
        self.formatter = DisplayFormatter()
    
    def get_pokemon_data(self, name_or_id: str) -> Dict[str, Any]:
        """Fetch Pokemon data from API"""
        return self.api_client.get_pokemon_data(name_or_id)
    
    def display_pokemon(self, data: Dict[str, Any]) -> None:
        """Display Pokemon information in a formatted way with proper alignment"""
        try:
            pokemon = data['pokemon']
            species = data['species']
            abilities_detail = data.get('abilities_detail', [])

            name = pokemon['name'].title()
            id_num = pokemon['id']
            height = pokemon['height'] / 10  # Convert to meters
            weight = pokemon['weight'] / 10  # Convert to kg
            types = self.formatter.format_types(pokemon['types'])
            description = self.formatter.get_description(species)
            stats = self.formatter.format_stats(pokemon['stats'])

            # Get abilities with descriptions
            ability_descriptions = self.formatter.get_ability_descriptions(abilities_detail)

            # Get additional info
            egg_groups = self.formatter.get_egg_groups(species)
            growth_rate = self.formatter.get_growth_rate(species)
            optimal_nature = self.formatter.calculate_optimal_nature(pokemon['stats'])

            # Get sprite ASCII art
            sprite_url = None
            if 'sprites' in pokemon and pokemon['sprites']:
                sprite_url = pokemon['sprites'].get('front_default')

            if sprite_url:
                ascii_sprite = self.formatter.get_sprite_ascii(sprite_url, width=50)
            else:
                ascii_sprite = "No sprite available"
            
            sprite_lines = ascii_sprite.split('\n')
            
            # Match the header width - total content width is 113 chars
            sprite_width = 50  # Left side for sprite
            info_width = 60    # Right side for info (50 + 3 for " │ " + 60 = 113)
            
            # Ensure sprite lines are consistent width
            sprite_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite_lines]
            
            # Pad sprite to minimum height if needed
            min_sprite_height = 20
            while len(sprite_lines) < min_sprite_height:
                sprite_lines.append(" " * sprite_width)

            # Build info section with proper text wrapping
            info_lines = []
            
            # Basic info - handle long lines carefully
            height_weight = f"Height: {height:.1f}m | Weight: {weight:.1f}kg"
            info_lines.extend(self.formatter.wrap_text(height_weight, info_width))
            
            info_lines.extend(self.formatter.wrap_text(f"Egg Groups: {egg_groups}", info_width))
            info_lines.extend(self.formatter.wrap_text(f"Growth Rate: {growth_rate}", info_width))
            
            # Handle nature which can be long
            nature_lines = self.formatter.wrap_text(f"Optimal Nature: {optimal_nature}", info_width)
            info_lines.extend(nature_lines)
            info_lines.append("")
            
            # Abilities
            info_lines.append("ABILITIES:")
            for ability_desc in ability_descriptions:
                wrapped_ability = self.formatter.wrap_text(ability_desc, info_width)
                info_lines.extend(wrapped_ability)
            info_lines.append("")
            
            # Description
            info_lines.append("DESCRIPTION:")
            description_lines = self.formatter.wrap_text(description, info_width)
            info_lines.extend(description_lines)
            info_lines.append("")
            
            # Base stats
            info_lines.append("BASE STATS:")
            stat_lines = stats.split('\n')
            info_lines.extend(stat_lines)
            
            # Ensure info lines are consistent width - truncate and pad to exact width
            info_lines = [line[:info_width].ljust(info_width) for line in info_lines]
            
            # Make both sections the same height
            max_height = max(len(sprite_lines), len(info_lines))
            
            # Pad shorter section
            while len(sprite_lines) < max_height:
                sprite_lines.append(" " * sprite_width)
            while len(info_lines) < max_height:
                info_lines.append(" " * info_width)

            # Build the header line manually to handle ANSI codes properly
            # Calculate the exact spacing needed
            name_section = f"#{id_num:03d} - {name}"  # Name without padding
            type_section = f"Type: {types}"
            
            # Remove ANSI codes to calculate visible length of type section
            type_section_visible = re.sub(r'\033\[[0-9;]*m', '', type_section)
            
            # Calculate spacing needed between name and type to right-align type
            # Total content width is 113, account for borders and spacing
            available_space = 113 - len(name_section) - len(type_section_visible)
            padding = ' ' * max(0, available_space)
            
            header_line = f"║ {name_section}{padding}{type_section} ║"

            # Display header
            print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                    POKÉDX ENTRY                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
{header_line}
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣""")

            # Display sprite and info side by side with proper alignment
            for i in range(max_height):
                sprite_part = sprite_lines[i]
                info_part = info_lines[i]
                print(f"║ {sprite_part} │ {info_part} ║")

            print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")

        except Exception as e:
            print(f"Error in display_pokemon: {e}")
            # Fallback to basic display
            if data and 'pokemon' in data:
                pokemon = data['pokemon']
                print(f"Pokemon: {pokemon.get('name', 'Unknown')}")
                print(f"ID: {pokemon.get('id', 'Unknown')}")

    def search_pokemon(self, query: str) -> None:
        """Search for a Pokemon and display its information"""
        print(f"\n🔍 Searching for: {query}")
        print("Loading...")

        data = self.get_pokemon_data(query)

        if data is None:
            print(f"\n❌ Pokemon '{query}' not found!")
            print("Try searching by name (e.g., 'pikachu') or ID number (e.g., '25')")
            return

        self.display_pokemon(data)