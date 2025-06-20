# display_utils.py
"""
Display formatting utilities for the Pokédex Terminal App
"""

import re
import requests
from PIL import Image
import io
from typing import Dict, Any, List
from config import TYPE_COLORS, CATEGORY_COLORS, ASCII_CHARS, STAT_NAMES, NATURES

class DisplayFormatter:
    """Handles all display formatting and ASCII art generation"""
    
    def __init__(self):
        self.ascii_chars = ASCII_CHARS
    
    def wrap_text(self, text: str, width: int) -> List[str]:
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
    
    def format_move_type(self, move_type: str) -> str:
        """Format move type with colors - returns fixed width"""
        color = TYPE_COLORS.get(move_type.lower(), '37')
        # Format to exactly 8 characters visible width, then add color
        type_text = move_type.upper()[:8].ljust(8)
        return f"\033[{color}m{type_text}\033[0m"

    def format_move_category(self, category: str) -> str:
        """Format move category with colors - returns fixed width"""
        color = CATEGORY_COLORS.get(category.lower(), '37')
        # Format to exactly 8 characters visible width, then add color
        category_text = category[:8].ljust(8)
        return f"\033[{color}m{category_text}\033[0m"
    
    def format_types(self, types: list) -> str:
        """Format Pokemon types with colors"""
        colored_types = []
        for type_info in types:
            type_name = type_info['type']['name']
            color = TYPE_COLORS.get(type_name, '37')
            colored_types.append(f"\033[{color}m{type_name.upper()}\033[0m")
        return " / ".join(colored_types)
    
    def format_stats(self, stats: list) -> str:
        """Format Pokemon stats in a nice table"""
        formatted_stats = []
        for stat in stats:
            name = STAT_NAMES.get(stat['stat']['name'], stat['stat']['name'])
            value = stat['base_stat']
            # Create a simple bar visualization
            bar = '█' * (value // 10) + '░' * (15 - value // 10)
            formatted_stats.append(f"  {name:<8}: {value:>3} {bar}")
        return "\n".join(formatted_stats)
    
    def calculate_optimal_nature(self, stats: list) -> str:
        """Calculate the best nature based on highest/lowest base stats"""
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
        for nature, (boost, reduce) in NATURES.items():
            if boost == highest_stat and reduce == lowest_stat:
                return f"{nature} (+{boost.replace('-', ' ').title()}, -{reduce.replace('-', ' ').title()})"

        # If no perfect match, find one that at least boosts the highest stat
        for nature, (boost, reduce) in NATURES.items():
            if boost == highest_stat:
                return f"{nature} (+{boost.replace('-', ' ').title()}, -{reduce.replace('-', ' ').title()})"

        return "Hardy (Neutral)"
    
    def get_sprite_ascii(self, sprite_url: str, width: int = 50) -> str:
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
    
    def format_bordered_content(self, lines: List[str], content_width: int = 113) -> List[str]:
        """Format content lines to fit within bordered display"""
        formatted_lines = []
        for line in lines:
            # Calculate visible length (excluding ANSI codes)
            visible_line = re.sub(r'\033\[[0-9;]*m', '', line)
            visible_length = len(visible_line)
            
            # Pad the line to exact visible width
            padding_needed = max(0, content_width - visible_length)
            formatted_line = line + (' ' * padding_needed)
            formatted_lines.append(f"║ {formatted_line} ║")
        
        return formatted_lines