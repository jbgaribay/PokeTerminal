# move_handler.py
"""
Move data handling and display for the Pokédex Terminal App
"""

from typing import Dict, Any, List
from api_client import PokeAPIClient
from display_utils import DisplayFormatter
from config import GEN_VERSION_GROUPS, ROMAN_TO_INT

class MoveHandler:
    """Handles move data fetching and display"""
    
    def __init__(self):
        self.api_client = PokeAPIClient()
        self.formatter = DisplayFormatter()
    
    def handle_move_query(self, query: str, pokemon_data: Dict[str, Any]) -> None:
        """Handle move-related query parsing and execution"""
        try:
            # Parse the query to extract command, generation, and optional game
            # Expected formats: 
            # "moves gen 3", "moves gen 3 emerald"
            # "learnset gen 4", "tm gen 3 emerald", etc.
            
            parts = query.lower().split()
            
            if len(parts) < 3:  # Need at least: command + "gen" + number
                print("❌ Invalid format! Use: <command> gen <number> [game]")
                print("   Examples: 'moves gen 3', 'tm gen 3 emerald', 'learnset gen 4 platinum'")
                return
            
            command = parts[0]  # moves, learnset, tm, egg, tutor
            gen_word = parts[1]  # should be "gen"
            gen_str = parts[2]   # generation number
            
            if gen_word != "gen":
                print("❌ Invalid format! Use: <command> gen <number> [game]")
                return
            
            # Parse generation number
            try:
                generation = int(gen_str)
                if generation < 1 or generation > 9:
                    print("❌ Generation must be between 1 and 9!")
                    return
            except ValueError:
                print("❌ Invalid generation number!")
                return
            
            # Extract optional game name
            specific_game = None
            if len(parts) > 3:
                specific_game = "-".join(parts[3:])  # Handle multi-word games like "ultra-sun-ultra-moon"
            
            print(f"\n🔍 Loading {command} data for {pokemon_data['name'].title()} (Generation {generation}" + 
                  (f", {specific_game.title()}" if specific_game else "") + ")...")
            
            # Get move data
            moves_data = self.get_learnset_data(pokemon_data, generation, specific_game)
            
            if not moves_data:
                print("❌ Could not load move data")
                return
            
            # Display the appropriate moves based on command
            self.display_specific_moves(pokemon_data['name'], generation, command, moves_data)
            
        except Exception as e:
            print(f"❌ Error processing move query: {e}")
    
    def get_learnset_data(self, pokemon_data: Dict[str, Any], generation: int, specific_game: str = None) -> Dict[str, Any]:
        """Fetch learnset data for a specific generation and optionally a specific game"""
        try:
            moves_data = {
                'level_up': [],
                'tm_hm': [],
                'egg': [],
                'tutor': []
            }
            
            # Determine which version groups to include
            if specific_game and specific_game in GEN_VERSION_GROUPS.get(generation, {}):
                target_version_groups = GEN_VERSION_GROUPS[generation][specific_game]
                game_filter_text = specific_game.replace('-', ' ').title()
            else:
                target_version_groups = GEN_VERSION_GROUPS.get(generation, {}).get('all', [])
                game_filter_text = f"Generation {generation}"
            
            for move_entry in pokemon_data.get('moves', []):
                move_name = move_entry['move']['name']
                move_url = move_entry['move']['url']
                
                # Get detailed move information
                move_details = self.api_client.get_move_details(move_url)
                if not move_details:
                    continue
                
                # Check if move exists in specified generation
                move_generation = move_details.get('generation', {}).get('name', '')
                
                gen_number = 999  # Default for unknown generations
                if move_generation:
                    gen_part = move_generation.split('-')[-1].lower()
                    gen_number = ROMAN_TO_INT.get(gen_part, 999)
                
                if gen_number > generation:
                    continue
                
                # Process version group details for the specified generation/game
                for version_detail in move_entry.get('version_group_details', []):
                    version_group = version_detail['version_group']['name']
                    learn_method = version_detail['move_learn_method']['name']
                    level_learned = version_detail.get('level_learned_at', 0)
                    
                    # Check if this version group matches our target
                    if version_group not in target_version_groups:
                        continue
                    
                    # Organize by learn method
                    move_info = {
                        'name': move_name.replace('-', ' ').title(),
                        'type': move_details.get('type', {}).get('name', 'unknown'),
                        'power': move_details.get('power'),
                        'accuracy': move_details.get('accuracy'),
                        'pp': move_details.get('pp'),
                        'level': level_learned,
                        'category': move_details.get('damage_class', {}).get('name', 'unknown'),
                        'version_group': version_group
                    }
                    
                    if learn_method == 'level-up':
                        moves_data['level_up'].append(move_info)
                    elif learn_method in ['machine', 'tm']:
                        moves_data['tm_hm'].append(move_info)
                    elif learn_method == 'egg':
                        moves_data['egg'].append(move_info)
                    elif learn_method == 'tutor':
                        moves_data['tutor'].append(move_info)
            
            # Sort level-up moves by level
            moves_data['level_up'].sort(key=lambda x: x['level'])
            
            # Remove duplicates (keep the first occurrence)
            for category in moves_data:
                seen = set()
                unique_moves = []
                for move in moves_data[category]:
                    move_key = move['name']
                    if move_key not in seen:
                        seen.add(move_key)
                        unique_moves.append(move)
                moves_data[category] = unique_moves
            
            # Add metadata about the filter applied
            moves_data['filter_info'] = {
                'generation': generation,
                'game': specific_game,
                'display_name': game_filter_text
            }
            
            return moves_data
            
        except Exception as e:
            print(f"Error fetching learnset data: {e}")
            return None
    
    def format_move_table(self, moves: list, title: str) -> str:
        """Format moves in a nice table"""
        if not moves:
            return f"{title}: None"
        
        lines = [f"{title}:"]
        lines.append("─" * 80)
        
        # Add column headers
        if any('level' in move and move['level'] > 0 for move in moves):
            # Level-up moves have level column
            header = f"{'LEVEL':<5} {'MOVE NAME':<20} {'TYPE':<8} {'POW':<4} {'ACC':<4} {'PP':<3} {'CATEGORY':<8}"
        else:
            # Other moves don't have level column
            header = f"{'     '} {'MOVE NAME':<20} {'TYPE':<8} {'POW':<4} {'ACC':<4} {'PP':<3} {'CATEGORY':<8}"
        
        lines.append(header)
        lines.append("─" * 80)
        
        for move in moves[:20]:  # Limit to first 20 moves to avoid overwhelming output
            name = move['name'][:20].ljust(20)  # Truncate long names
            move_type = self.formatter.format_move_type(move['type'])
            power = str(move['power'] or '--').ljust(4)
            accuracy = str(move['accuracy'] or '--').ljust(4)
            pp = str(move['pp'] or '--').ljust(3)
            category = self.formatter.format_move_category(move['category'])
            
            if 'level' in move and move['level'] > 0:
                level = f"Lv.{move['level']:>2}".ljust(5)
                line = f"{level} {name} {move_type} {power} {accuracy} {pp} {category}"
            else:
                line = f"     {name} {move_type} {power} {accuracy} {pp} {category}"
            
            lines.append(line)
        
        if len(moves) > 20:
            lines.append(f"... and {len(moves) - 20} more moves")
        
        return '\n'.join(lines)
    
    def display_specific_moves(self, pokemon_name: str, generation: int, move_type: str, moves_data: Dict[str, Any]) -> None:
        """Display specific type of moves (level-up, egg, etc.) in a formatted way"""
        try:
            # Map command to data key and display title
            move_categories = {
                'learnset': ('level_up', 'LEVEL-UP MOVES'),
                'tm': ('tm_hm', 'TM/HM MOVES'), 
                'egg': ('egg', 'EGG MOVES'),
                'tutor': ('tutor', 'MOVE TUTOR'),
                'moves': ('all', 'ALL MOVES')  # Special case for showing everything
            }
            
            if move_type not in move_categories:
                print(f"❌ Unknown move type: {move_type}")
                return
                
            data_key, title = move_categories[move_type]
            
            # Handle the 'moves' command (show all categories)
            if move_type == 'moves':
                self.display_learnset(pokemon_name, generation, moves_data)
                return
            
            # Get filter info for display
            filter_info = moves_data.get('filter_info', {})
            display_name = filter_info.get('display_name', f'Generation {generation}')
            
            # Show specific move category only
            moves = moves_data.get(data_key, [])
            
            print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                     {pokemon_name.upper()} - {display_name.upper()} {title}                                     ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣""")
            
            if not moves:
                # No moves found message
                no_moves_msg = f"No {title.lower()} found for {display_name}"
                content_width = 113
                formatted_line = no_moves_msg[:content_width].ljust(content_width)
                print(f"║ {formatted_line} ║")
            else:
                # Format and display moves - but ONLY this category
                move_table = self.format_move_table(moves, title)
                content_lines = move_table.split('\n')
                
                # Use formatter to handle bordered content
                formatted_lines = self.formatter.format_bordered_content(content_lines)
                for line in formatted_lines:
                    print(line)
            
            print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            print(f"Error displaying {move_type} moves: {e}")

    def display_learnset(self, pokemon_name: str, generation: int, moves_data: Dict[str, Any]) -> None:
        """Display Pokemon learnset in a formatted way"""
        try:
            # Get filter info for display
            filter_info = moves_data.get('filter_info', {})
            display_name = filter_info.get('display_name', f'Generation {generation}')
            
            print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                           {pokemon_name.upper()} - {display_name.upper()} LEARNSET                                           ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣""")
            
            # Build learnset content
            content_lines = []
            
            # Level-up moves
            if moves_data['level_up']:
                level_moves = self.format_move_table(moves_data['level_up'], "LEVEL-UP MOVES")
                content_lines.extend(level_moves.split('\n'))
                content_lines.append("")
            
            # TM/HM moves
            if moves_data['tm_hm']:
                tm_moves = self.format_move_table(moves_data['tm_hm'], "TM/HM MOVES")
                content_lines.extend(tm_moves.split('\n'))
                content_lines.append("")
            
            # Egg moves
            if moves_data['egg']:
                egg_moves = self.format_move_table(moves_data['egg'], "EGG MOVES")
                content_lines.extend(egg_moves.split('\n'))
                content_lines.append("")
            
            # Tutor moves
            if moves_data['tutor']:
                tutor_moves = self.format_move_table(moves_data['tutor'], "MOVE TUTOR")
                content_lines.extend(tutor_moves.split('\n'))
            
            # Use formatter to handle bordered content
            formatted_lines = self.formatter.format_bordered_content(content_lines)
            for line in formatted_lines:
                print(line)
            
            print("╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            print(f"Error displaying learnset: {e}")