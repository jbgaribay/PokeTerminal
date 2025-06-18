#!/usr/bin/env python3
"""
Pokédex Terminal App
A simple command-line Pokédex that fetches data from PokéAPI
"""

import requests
import json
from typing import Dict, Any, Optional
import sys
from PIL import Image
import io

class Pokedex:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2/pokemon/"
        self.species_url = "https://pokeapi.co/api/v2/pokemon-species/"
        # ASCII characters for different brightness levels (expanded for more detail)
        self.ascii_chars = "@@%%##**++==--::..  "

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

    def wrap_text(self, text, width):
        """Wrap text to specified width, handling word boundaries"""
        if not text:
            return [""]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Handle very long words
                    lines.append(word[:width])
                    current_line = word[width:]
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]

    def get_description(self, species_data: Dict[str, Any]) -> str:
        """Extract English description from species data"""
        if not species_data or 'flavor_text_entries' not in species_data:
            return "No description available."
        
        # Find English flavor text
        for entry in species_data['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                # Clean up the text (remove special characters)
                text = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                return ' '.join(text.split())
        
        return "No description available."

    def get_ability_descriptions(self, abilities_data: list) -> list:
        """Extract ability descriptions as a list of strings"""
        if not abilities_data:
            return ["No abilities available."]
        
        descriptions = []
        for ability_data in abilities_data:
            name = ability_data.get('name', 'Unknown').title()
            # Find English description
            description = "No description available."
            for entry in ability_data.get('flavor_text_entries', []):
                if entry['language']['name'] == 'en':
                    description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                    description = ' '.join(description.split())
                    break
            descriptions.append(f"{name}: {description}")
        
        return descriptions

    def get_egg_groups(self, species_data: Dict[str, Any]) -> str:
        """Extract egg groups"""
        if not species_data or 'egg_groups' not in species_data:
            return "Unknown"

        groups = [group['name'].title() for group in species_data['egg_groups']]
        return ", ".join(groups)

    def get_growth_rate(self, species_data: Dict[str, Any]) -> str:
        """Extract growth rate"""
        if not species_data or 'growth_rate' not in species_data:
            return "Unknown"

        return species_data['growth_rate']['name'].replace('-', ' ').title()

    def calculate_optimal_nature(self, stats: list) -> str:
        """Calculate the best nature based on highest/lowest base stats"""
        # Nature effects: {nature: (boosted_stat, reduced_stat)}
        natures = {
            'Adamant': ('attack', 'special-attack'),
            'Bold': ('defense', 'attack'),
            'Brave': ('attack', 'speed'),
            'Calm': ('special-defense', 'attack'),
            'Careful': ('special-defense', 'special-attack'),
            'Hasty': ('speed', 'defense'),
            'Impish': ('defense', 'special-attack'),
            'Jolly': ('speed', 'special-attack'),
            'Lax': ('defense', 'special-defense'),
            'Lonely': ('attack', 'defense'),
            'Mild': ('special-attack', 'defense'),
            'Modest': ('special-attack', 'attack'),
            'Naive': ('speed', 'special-defense'),
            'Naughty': ('attack', 'special-defense'),
            'Quiet': ('special-attack', 'speed'),
            'Rash': ('special-attack', 'special-defense'),
            'Relaxed': ('defense', 'speed'),
            'Sassy': ('special-defense', 'speed'),
            'Timid': ('speed', 'attack'),
        }

        # Create stat dictionary (excluding HP as it's never affected by nature)
        stat_dict = {}
        for stat in stats:
            stat_name = stat['stat']['name']
            if stat_name != 'hp':
                stat_dict[stat_name] = stat['base_stat']

        # Find highest and lowest stats
        highest_stat = max(stat_dict, key=stat_dict.get)
        lowest_stat = min(stat_dict, key=stat_dict.get)

        # Find nature that boosts highest and reduces lowest
        for nature, (boost, reduce) in natures.items():
            if boost == highest_stat and reduce == lowest_stat:
                return f"{nature} (+{boost.replace('-', ' ').title()}, -{reduce.replace('-', ' ').title()})"

        # If no perfect match, find one that at least boosts the highest stat
        for nature, (boost, reduce) in natures.items():
            if boost == highest_stat:
                return f"{nature} (+{boost.replace('-', ' ').title()}, -{reduce.replace('-', ' ').title()})"

        return "Hardy (Neutral)"

    def get_sprite_ascii(self, sprite_url: str, width: int = 60) -> str:
        """Convert Pokemon sprite to ASCII art"""
        try:
            if not sprite_url:
                return "No sprite available"

            # Download the sprite image
            response = requests.get(sprite_url)
            if response.status_code != 200:
                return "Failed to load sprite"

            # Open image with PIL
            img = Image.open(io.BytesIO(response.content))

            # Convert to RGBA first to handle transparency properly
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Create a white background to handle transparency
            background = Image.new('RGBA', img.size, (255, 255, 255, 255))
            img = Image.alpha_composite(background, img)

            # Convert to grayscale
            img = img.convert('L')

            # Calculate new height to maintain aspect ratio
            aspect_ratio = img.height / img.width
            height = int(width * aspect_ratio * 0.45)  # Adjusted for better proportions

            # Resize image
            img = img.resize((width, height))

            # Convert to ASCII
            ascii_lines = []
            for y in range(height):
                line = ""
                for x in range(width):
                    pixel = img.getpixel((x, y))
                    # Map pixel brightness to ASCII character
                    ascii_index = int(pixel / 255 * (len(self.ascii_chars) - 1))
                    line += self.ascii_chars[ascii_index]
                ascii_lines.append(line)

            return "\n".join(ascii_lines)

        except Exception as e:
            return f"Error generating ASCII art: {str(e)}"

    def format_types(self, types: list) -> str:
        """Format Pokemon types with colors"""
        type_colors = {
            'normal': '37',    # white
            'fire': '91',      # red
            'water': '94',     # blue
            'electric': '93',  # yellow
            'grass': '92',     # green
            'ice': '96',       # cyan
            'fighting': '31',  # dark red
            'poison': '95',    # magenta
            'ground': '33',    # yellow/brown
            'flying': '36',    # dark cyan
            'psychic': '35',   # magenta
            'bug': '32',       # green
            'rock': '33',      # yellow
            'ghost': '35',     # magenta
            'dragon': '34',    # blue
            'dark': '90',      # dark gray
            'steel': '37',     # white
            'fairy': '95',     # bright magenta
        }

        colored_types = []
        for type_info in types:
            type_name = type_info['type']['name']
            color = type_colors.get(type_name, '37')
            colored_types.append(f"\033[{color}m{type_name.upper()}\033[0m")

        return " / ".join(colored_types)

    def format_stats(self, stats: list) -> str:
        """Format Pokemon stats in a nice table"""
        stat_names = {
            'hp': 'HP',
            'attack': 'Attack',
            'defense': 'Defense',
            'special-attack': 'Sp. Atk',
            'special-defense': 'Sp. Def',
            'speed': 'Speed'
        }

        formatted_stats = []
        for stat in stats:
            name = stat_names.get(stat['stat']['name'], stat['stat']['name'])
            value = stat['base_stat']
            # Create a simple bar visualization
            bar = '█' * (value // 10) + '░' * (15 - value // 10)
            formatted_stats.append(f"  {name:<8}: {value:>3} {bar}")

        return "\n".join(formatted_stats)

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
            types = self.format_types(pokemon['types'])
            description = self.get_description(species)
            stats = self.format_stats(pokemon['stats'])

            # Get abilities with descriptions
            abilities = []
            if 'abilities' in pokemon and pokemon['abilities']:
                abilities = [ability['ability']['name'].title() for ability in pokemon['abilities']]
            abilities_str = ", ".join(abilities) if abilities else "Unknown"
            ability_descriptions = self.get_ability_descriptions(abilities_detail)

            # Get additional info
            egg_groups = self.get_egg_groups(species)
            growth_rate = self.get_growth_rate(species)
            optimal_nature = self.calculate_optimal_nature(pokemon['stats'])

            # Get sprite ASCII art
            sprite_url = None
            if 'sprites' in pokemon and pokemon['sprites']:
                sprite_url = pokemon['sprites'].get('front_default')

            if sprite_url:
                ascii_sprite = self.get_sprite_ascii(sprite_url, width=50)
            else:
                ascii_sprite = "No sprite available"
            
            sprite_lines = ascii_sprite.split('\n')
            
            # Match the header width - total content width is 113 chars
            # Header line: "║ #006 - Charizard                                    Type: FIRE / FLYING                                                   ║"
            # Content after "║ " and before " ║" = 113 characters
            
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
            info_lines.extend(self.wrap_text(height_weight, info_width))
            
            info_lines.extend(self.wrap_text(f"Egg Groups: {egg_groups}", info_width))
            info_lines.extend(self.wrap_text(f"Growth Rate: {growth_rate}", info_width))
            
            # Handle nature which can be long
            nature_lines = self.wrap_text(f"Optimal Nature: {optimal_nature}", info_width)
            info_lines.extend(nature_lines)
            info_lines.append("")
            
            # Abilities
            info_lines.append("ABILITIES:")
            for ability_desc in ability_descriptions:
                wrapped_ability = self.wrap_text(ability_desc, info_width)
                info_lines.extend(wrapped_ability)
            info_lines.append("")
            
            # Description
            info_lines.append("DESCRIPTION:")
            description_lines = self.wrap_text(description, info_width)
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
            import re
            
            # Calculate the exact spacing needed
            name_section = f"#{id_num:03d} - {name:<50}"  # This part is 55 chars
            type_section_start = "Type: "  # 6 chars
            
            # Remove ANSI codes to calculate visible length
            types_visible = re.sub(r'\033\[[0-9;]*m', '', types)
            
            # Calculate remaining space: total 113 chars - 55 (name) - 6 (Type: ) - visible types length
            # Subtract 2-3 more to account for small discrepancies
            remaining_space = 113 - 55 - 6 - len(types_visible) - 3
            padding = ' ' * max(0, remaining_space)  # Ensure no negative padding
            
            header_line = f"║ {name_section} {type_section_start}{types}{padding} ║"

            # Display header
            print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                    POKÉDEX ENTRY                                                  ║
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

    def run(self):
        """Main application loop"""
        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              POKÉDEX TERMINAL                                 ║
║                         Gotta catch 'em all!                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Welcome to the Pokédex Terminal!
Search for any Pokémon by name or ID number.
Type 'quit' or 'exit' to close the application.

        """)

        while True:
            try:
                query = input("\n🔍 Enter Pokémon name or ID: ").strip()

                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nThanks for using Pokédex Terminal! Goodbye! 👋")
                    break

                if not query:
                    print("Please enter a Pokémon name or ID.")
                    continue

                self.search_pokemon(query)

            except KeyboardInterrupt:
                print("\n\nThanks for using Pokédex Terminal! Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.")

def main():
    """Entry point of the application"""
    try:
        pokedex = Pokedex()
        pokedex.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)

if __name__ == "__main__":
    main()