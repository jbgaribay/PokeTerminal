# evolution_handler.py
"""
Evolution chain handling and display for the Pokédex Terminal App
"""

import requests
from typing import Dict, Any, List, Optional, Tuple
from api_client import PokeAPIClient
from display_utils import DisplayFormatter

class EvolutionHandler:
    """Handles evolution chain data fetching and ASCII display"""
    
    def __init__(self):
        self.api_client = PokeAPIClient()
        self.formatter = DisplayFormatter()
    
    def get_evolution_chain_data(self, pokemon_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch evolution chain data for a Pokemon"""
        try:
            # Get species data first to get evolution chain URL
            species_id = pokemon_data.get('species', {}).get('url', '').split('/')[-2]
            if not species_id:
                return None
            
            species_response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{species_id}")
            if species_response.status_code != 200:
                return None
            
            species_data = species_response.json()
            evolution_chain_url = species_data.get('evolution_chain', {}).get('url')
            
            if not evolution_chain_url:
                return None
            
            # Get evolution chain data
            evolution_response = requests.get(evolution_chain_url)
            if evolution_response.status_code != 200:
                return None
            
            return evolution_response.json()
            
        except Exception as e:
            print(f"Error fetching evolution chain: {e}")
            return None
    
    def parse_evolution_chain(self, chain_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse evolution chain data into a structured format"""
        try:
            chain = chain_data.get('chain', {})
            evolution_stages = []
            
            def parse_stage(stage_data, stage_number=1):
                """Recursively parse each evolution stage"""
                species_name = stage_data.get('species', {}).get('name', '')
                
                # Get evolution details
                evolution_details = stage_data.get('evolution_details', [])
                evolution_trigger = None
                evolution_level = None
                evolution_item = None
                evolution_condition = None
                
                if evolution_details:
                    detail = evolution_details[0]  # Take first evolution method
                    evolution_trigger = detail.get('trigger', {}).get('name', '')
                    evolution_level = detail.get('min_level')
                    
                    # Check for items
                    if detail.get('item'):
                        evolution_item = detail.get('item', {}).get('name', '').replace('-', ' ').title()
                    
                    # Check for other conditions
                    if detail.get('min_happiness'):
                        evolution_condition = f"Happiness {detail.get('min_happiness')}"
                    elif detail.get('time_of_day'):
                        evolution_condition = f"{detail.get('time_of_day').title()} time"
                    elif detail.get('known_move'):
                        move_name = detail.get('known_move', {}).get('name', '').replace('-', ' ').title()
                        evolution_condition = f"Knows {move_name}"
                    elif detail.get('location'):
                        location_name = detail.get('location', {}).get('name', '').replace('-', ' ').title()
                        evolution_condition = f"At {location_name}"
                
                stage_info = {
                    'name': species_name,
                    'stage': stage_number,
                    'trigger': evolution_trigger,
                    'level': evolution_level,
                    'item': evolution_item,
                    'condition': evolution_condition,
                    'pokemon_data': None  # Will be filled later
                }
                
                evolution_stages.append(stage_info)
                
                # Process next evolutions
                for evolves_to in stage_data.get('evolves_to', []):
                    parse_stage(evolves_to, stage_number + 1)
            
            parse_stage(chain)
            return evolution_stages
            
        except Exception as e:
            print(f"Error parsing evolution chain: {e}")
            return []
    
    def get_pokemon_sprites(self, evolution_stages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fetch Pokemon data and sprites for each evolution stage"""
        try:
            enhanced_stages = []
            
            for stage in evolution_stages:
                pokemon_name = stage['name']
                
                # Get Pokemon data
                pokemon_data = self.api_client.get_pokemon_data(pokemon_name)
                if pokemon_data:
                    stage['pokemon_data'] = pokemon_data['pokemon']
                    # Don't generate ASCII here - we'll do it in display with proper sizing
                else:
                    stage['pokemon_data'] = None
                
                enhanced_stages.append(stage)
            
            return enhanced_stages
            
        except Exception as e:
            print(f"Error getting Pokemon sprites: {e}")
            return evolution_stages
    
    def format_evolution_requirement(self, stage: Dict[str, Any]) -> str:
        """Format the evolution requirement text"""
        if stage['stage'] == 1:
            return ""  # Base form has no evolution requirement
        
        trigger = stage.get('trigger', '')
        level = stage.get('level')
        item = stage.get('item')
        condition = stage.get('condition')
        
        if trigger == 'level-up':
            if level:
                req_text = f"LEVEL {level}"
            else:
                req_text = "LEVEL UP"
            
            if condition:
                req_text += f"\n{condition}"
        elif trigger == 'use-item':
            if item:
                req_text = f"USE {item.upper()}"
            else:
                req_text = "USE ITEM"
        elif trigger == 'trade':
            req_text = "TRADE"
            if item:
                req_text += f"\nwith {item}"
            if condition:
                req_text += f"\n{condition}"
        else:
            req_text = trigger.replace('-', ' ').upper() if trigger else "???"
            if condition:
                req_text += f"\n{condition}"
        
        return req_text
    
    def display_evolution_chain(self, pokemon_name: str, evolution_stages: List[Dict[str, Any]]) -> None:
        """Display the evolution chain with ASCII sprites and arrows"""
        try:
            if not evolution_stages:
                print("❌ No evolution data found")
                return
            
            # Sort stages by stage number
            stages = sorted(evolution_stages, key=lambda x: x['stage'])
            
            # Use EVEN WIDER border for evolution chains - 220 characters!
            border_width = 220
            
            print(f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                            {pokemon_name.upper()} - EVOLUTION CHAIN                                                                                            ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣""")
            
            if len(stages) == 1:
                # No evolutions
                single_stage = stages[0]
                pokemon_display_name = single_stage['name'].title()
                
                print("║" + " " * (border_width-2) + "║")
                no_evo_text = f"{pokemon_display_name} does not evolve"
                no_evo_line = no_evo_text.center(border_width-2)
                print(f"║ {no_evo_line} ║")
                print("║" + " " * (border_width-2) + "║")
                
                # Display single large sprite
                if single_stage.get('pokemon_data'):
                    sprite_url = single_stage['pokemon_data'].get('sprites', {}).get('front_default')
                    if sprite_url:
                        large_sprite = self.formatter.get_sprite_ascii(sprite_url, width=80)
                        sprite_lines = large_sprite.split('\n')
                        for line in sprite_lines[:30]:  # Limit height
                            padded_line = line[:80].center(border_width-2)
                            print(f"║ {padded_line} ║")
                
            else:
                # Multiple stages - display evolution chain
                self._display_evolution_stages_wide(stages, border_width)
            
            print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            
        except Exception as e:
            print(f"Error displaying evolution chain: {e}")
    
    def _display_evolution_stages_wide(self, stages: List[Dict[str, Any]], border_width: int) -> None:
        """Display evolution stages with much wider layout"""
        try:
            # Calculate layout based on number of stages
            if len(stages) == 2:
                # Two stages: [Pokemon] -> [Pokemon]
                self._display_two_stage_evolution_wide(stages, border_width)
            elif len(stages) == 3:
                # Three stages: [Pokemon] -> [Pokemon] -> [Pokemon]
                self._display_three_stage_evolution_wide(stages, border_width)
            else:
                # More complex chains - display vertically
                self._display_complex_evolution_wide(stages, border_width)
                
        except Exception as e:
            print(f"Error displaying evolution stages: {e}")
    
    def _display_three_stage_evolution_wide(self, stages: List[Dict[str, Any]], border_width: int) -> None:
        """Display three-stage evolution horizontally with MASSIVE sprites"""
        stage1, stage2, stage3 = stages[0], stages[1], stages[2]
        
        # Generate MASSIVE sprites for incredible detail - 65 characters wide!
        sprite1_lines = ['No sprite available']
        sprite2_lines = ['No sprite available']
        sprite3_lines = ['No sprite available']
        
        if stage1.get('pokemon_data'):
            sprite_url = stage1['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite1_lines = self.formatter.get_sprite_ascii(sprite_url, width=65).split('\n')
        
        if stage2.get('pokemon_data'):
            sprite_url = stage2['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite2_lines = self.formatter.get_sprite_ascii(sprite_url, width=65).split('\n')
                
        if stage3.get('pokemon_data'):
            sprite_url = stage3['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite3_lines = self.formatter.get_sprite_ascii(sprite_url, width=65).split('\n')
        
        # EXTREMELY tall sprites for maximum detail - 40 lines!
        max_height = max(len(sprite1_lines), len(sprite2_lines), len(sprite3_lines), 40)
        sprite1_lines = (sprite1_lines + [''] * max_height)[:max_height]
        sprite2_lines = (sprite2_lines + [''] * max_height)[:max_height]
        sprite3_lines = (sprite3_lines + [''] * max_height)[:max_height]
        
        # Format sprites to consistent width (65 chars each)
        sprite_width = 65
        sprite1_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite1_lines]
        sprite2_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite2_lines]
        sprite3_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite3_lines]
        
        # Get evolution requirements
        evolution_req1 = self.format_evolution_requirement(stage2)
        evolution_req2 = self.format_evolution_requirement(stage3)
        
        # Get Pokemon names
        name1 = stage1['name'].title()
        name2 = stage2['name'].title()
        name3 = stage3['name'].title()
        
        # Lots of spacing at the top
        print("║" + " " * (border_width-2) + "║")
        print("║" + " " * (border_width-2) + "║")
        
        # Display names - perfectly centered above each massive sprite
        name_line = f"{name1:^65}      {name2:^65}      {name3:^65}"
        name_line = name_line.center(border_width-2)
        print(f"║ {name_line} ║")
        
        print("║" + " " * (border_width-2) + "║")
        
        # Now display the MASSIVE sprites with arrows positioned properly
        for i in range(max_height):
            sprite1_part = sprite1_lines[i]
            sprite2_part = sprite2_lines[i]
            sprite3_part = sprite3_lines[i]
            
            # Position arrows and requirements much lower - about 40% down the sprite
            arrow1_part = ""
            arrow2_part = ""
            
            # Place evolution requirements about 40% down the sprite
            if i == int(max_height * 0.4):  # Requirements line
                req1_text = evolution_req1.replace('\n', ' ') if evolution_req1 else ''
                req2_text = evolution_req2.replace('\n', ' ') if evolution_req2 else ''
                arrow1_part = f"{req1_text:^22}" if req1_text else " " * 22
                arrow2_part = f"{req2_text:^22}" if req2_text else " " * 22
            elif i == int(max_height * 0.4) + 1:  # Arrow line (right after requirements)
                arrow1_part = "   ════════════════►   "
                arrow2_part = "   ════════════════►   "
            elif i == int(max_height * 0.4) + 2:  # Extra spacing line
                arrow1_part = "                      "
                arrow2_part = "                      "
            else:
                arrow1_part = "                      "  # 22 spaces for arrow area
                arrow2_part = "                      "
            
            # Combine all parts with proper spacing
            # Layout: [65 chars sprite] [22 chars arrow] [65 chars sprite] [22 chars arrow] [65 chars sprite]
            # Total: 65 + 22 + 65 + 22 + 65 = 239 chars, but we'll center it in our 220 char border
            line = f"{sprite1_part}{arrow1_part}{sprite2_part}{arrow2_part}{sprite3_part}"
            
            # Since the total is wider than our border, we need to trim slightly or adjust spacing
            if len(line) > (border_width-2):
                # Slightly reduce arrow spacing
                arrow1_part = arrow1_part[:20]
                arrow2_part = arrow2_part[:20]
                line = f"{sprite1_part}{arrow1_part}{sprite2_part}{arrow2_part}{sprite3_part}"
            
            # Center the entire line in the wide border
            line = line.center(border_width-2)
            print(f"║ {line} ║")
        
        # More spacing at the bottom
        print("║" + " " * (border_width-2) + "║")
        print("║" + " " * (border_width-2) + "║")
    
    def _display_evolution_stages(self, stages: List[Dict[str, Any]]) -> None:
        """Display multiple evolution stages with arrows"""
        try:
            # Calculate layout based on number of stages
            if len(stages) == 2:
                # Two stages: [Pokemon] -> [Pokemon]
                self._display_two_stage_evolution(stages)
            elif len(stages) == 3:
                # Three stages: [Pokemon] -> [Pokemon] -> [Pokemon]
                self._display_three_stage_evolution(stages)
            else:
                # More complex chains - display vertically
                self._display_complex_evolution(stages)
                
        except Exception as e:
            print(f"Error displaying evolution stages: {e}")
    
    def _display_two_stage_evolution(self, stages: List[Dict[str, Any]]) -> None:
        """Display two-stage evolution horizontally"""
        stage1, stage2 = stages[0], stages[1]
        
        # Re-generate sprites with larger size for better visibility
        sprite1_lines = ['No sprite']
        sprite2_lines = ['No sprite']
        
        if stage1.get('pokemon_data'):
            sprite_url = stage1['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite1_lines = self.formatter.get_sprite_ascii(sprite_url, width=40).split('\n')
        
        if stage2.get('pokemon_data'):
            sprite_url = stage2['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite2_lines = self.formatter.get_sprite_ascii(sprite_url, width=40).split('\n')
        
        # Ensure consistent height (taller for better sprites)
        max_height = max(len(sprite1_lines), len(sprite2_lines), 20)
        sprite1_lines = (sprite1_lines + [''] * max_height)[:max_height]
        sprite2_lines = (sprite2_lines + [''] * max_height)[:max_height]
        
        # Format sprites to consistent width (40 chars each for two stages)
        sprite_width = 40
        sprite1_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite1_lines]
        sprite2_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite2_lines]
        
        # Get evolution requirement
        evolution_req = self.format_evolution_requirement(stage2)
        
        # Get Pokemon names
        name1 = stage1['name'].title()
        name2 = stage2['name'].title()
        
        print("║                                                                                                                 ║")
        
        # Display names aligned with sprites
        name_line = f"{name1:^40}               {name2:^40}"
        name_line = name_line.center(113)
        print(f"║ {name_line} ║")
        
        print("║                                                                                                                 ║")
        
        # Display sprites side by side with big ASCII arrow
        for i in range(max_height):
            sprite1_part = sprite1_lines[i]
            sprite2_part = sprite2_lines[i]
            
            # Create big ASCII arrow in the middle
            arrow_part = ""
            if i == 1:  # Evolution requirement line
                req_text = evolution_req.replace('\n', ' ') if evolution_req else ''
                arrow_part = f"{req_text:^33}" if req_text else " " * 33
            elif i == 2:  # Arrow line 1
                arrow_part = "        ═══════════════════►        "
            elif i == 3:  # Arrow line 2 (empty for spacing)
                arrow_part = "                                 "
            else:
                arrow_part = "                                 "
            
            # Combine sprites with arrow
            line = f"{sprite1_part}{arrow_part}{sprite2_part}"
            
            # Ensure the line fits exactly in the border (113 chars)
            if len(line) > 113:
                line = line[:113]
            else:
                line = line.ljust(113)
            
            print(f"║ {line} ║")
        
        print("║                                                                                                                 ║")
    
    def _display_three_stage_evolution(self, stages: List[Dict[str, Any]]) -> None:
        """Display three-stage evolution horizontally with much larger sprites"""
        stage1, stage2, stage3 = stages[0], stages[1], stages[2]
        
        # Generate much larger sprites for better detail
        sprite1_lines = ['No sprite']
        sprite2_lines = ['No sprite']
        sprite3_lines = ['No sprite']
        
        if stage1.get('pokemon_data'):
            sprite_url = stage1['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite1_lines = self.formatter.get_sprite_ascii(sprite_url, width=50).split('\n')
        
        if stage2.get('pokemon_data'):
            sprite_url = stage2['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite2_lines = self.formatter.get_sprite_ascii(sprite_url, width=50).split('\n')
                
        if stage3.get('pokemon_data'):
            sprite_url = stage3['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite3_lines = self.formatter.get_sprite_ascii(sprite_url, width=50).split('\n')
        
        # Much taller sprites for more detail
        max_height = max(len(sprite1_lines), len(sprite2_lines), len(sprite3_lines), 30)
        sprite1_lines = (sprite1_lines + [''] * max_height)[:max_height]
        sprite2_lines = (sprite2_lines + [''] * max_height)[:max_height]
        sprite3_lines = (sprite3_lines + [''] * max_height)[:max_height]
        
        # Much wider sprites (50 chars each for detailed ASCII)
        sprite_width = 50
        sprite1_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite1_lines]
        sprite2_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite2_lines]
        sprite3_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite3_lines]
        
        # Get evolution requirements
        evolution_req1 = self.format_evolution_requirement(stage2)
        evolution_req2 = self.format_evolution_requirement(stage3)
        
        # Get Pokemon names
        name1 = stage1['name'].title()
        name2 = stage2['name'].title()
        name3 = stage3['name'].title()
        
        # More spacing at the top
        print("║                                                                                                                 ║")
        print("║                                                                                                                 ║")
        print("║                                                                                                                 ║")
        
        # Display names - much higher up, aligned with sprites
        name_line = f"{name1:^50}   {name2:^50}   {name3:^50}"
        # Make sure the line fits in the border
        name_line = name_line[:113].ljust(113)
        print(f"║ {name_line} ║")
        
        print("║                                                                                                                 ║")
        
        # Now display the massive sprites with arrows positioned much lower
        for i in range(max_height):
            sprite1_part = sprite1_lines[i]
            sprite2_part = sprite2_lines[i]
            sprite3_part = sprite3_lines[i]
            
            # Position arrows and requirements much lower in the sprite area
            arrow1_part = ""
            arrow2_part = ""
            
            # Place evolution requirements about 1/3 down the sprite
            if i == max_height // 3:  # Requirements line (about 1/3 down)
                req1_text = evolution_req1.replace('\n', ' ') if evolution_req1 else ''
                req2_text = evolution_req2.replace('\n', ' ') if evolution_req2 else ''
                arrow1_part = f"{req1_text:^13}" if req1_text else " " * 13
                arrow2_part = f"{req2_text:^13}" if req2_text else " " * 13
            elif i == (max_height // 3) + 1:  # Arrow line (right after requirements)
                arrow1_part = " ══════════► "
                arrow2_part = " ══════════► "
            elif i == (max_height // 3) + 2:  # Extra spacing line
                arrow1_part = "             "
                arrow2_part = "             "
            else:
                arrow1_part = "             "  # 13 spaces to match arrow width
                arrow2_part = "             "
            
            # Combine all parts - now we have much more space
            line = f"{sprite1_part}{arrow1_part}{sprite2_part}{arrow2_part}{sprite3_part}"
            
            # Ensure the line fits (we now have 50+13+50+13+50 = 176 chars, need to fit in 113)
            # So we need to truncate or adjust spacing
            if len(line) > 113:
                # Reduce spacing between elements if needed
                line = f"{sprite1_part[:40]}{arrow1_part[:8]}{sprite2_part[:40]}{arrow2_part[:8]}{sprite3_part[:40]}"
                line = line[:113]
            
            line = line.ljust(113)
            print(f"║ {line} ║")
        
        # More spacing at the bottom
        print("║                                                                                                                 ║")
        print("║                                                                                                                 ║")
    
    def _display_two_stage_evolution_wide(self, stages: List[Dict[str, Any]], border_width: int) -> None:
        """Display two-stage evolution horizontally with ENORMOUS sprites"""
        stage1, stage2 = stages[0], stages[1]
        
        # Generate ENORMOUS sprites - 90 characters wide for two-stage!
        sprite1_lines = ['No sprite available']
        sprite2_lines = ['No sprite available']
        
        if stage1.get('pokemon_data'):
            sprite_url = stage1['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite1_lines = self.formatter.get_sprite_ascii(sprite_url, width=90).split('\n')
        
        if stage2.get('pokemon_data'):
            sprite_url = stage2['pokemon_data'].get('sprites', {}).get('front_default')
            if sprite_url:
                sprite2_lines = self.formatter.get_sprite_ascii(sprite_url, width=90).split('\n')
        
        # EXTREMELY tall sprites for maximum detail - 45 lines!
        max_height = max(len(sprite1_lines), len(sprite2_lines), 45)
        sprite1_lines = (sprite1_lines + [''] * max_height)[:max_height]
        sprite2_lines = (sprite2_lines + [''] * max_height)[:max_height]
        
        # Format sprites to consistent width (90 chars each)
        sprite_width = 90
        sprite1_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite1_lines]
        sprite2_lines = [line[:sprite_width].ljust(sprite_width) for line in sprite2_lines]
        
        # Get evolution requirement
        evolution_req = self.format_evolution_requirement(stage2)
        
        # Get Pokemon names
        name1 = stage1['name'].title()
        name2 = stage2['name'].title()
        
        # Lots of spacing at the top
        print("║" + " " * (border_width-2) + "║")
        print("║" + " " * (border_width-2) + "║")
        
        # Display names - perfectly centered above each enormous sprite
        name_line = f"{name1:^90}          {name2:^90}"
        name_line = name_line.center(border_width-2)
        print(f"║ {name_line} ║")
        
        print("║" + " " * (border_width-2) + "║")
        
        # Display the ENORMOUS sprites with big arrow
        for i in range(max_height):
            sprite1_part = sprite1_lines[i]
            sprite2_part = sprite2_lines[i]
            
            # Position arrow and requirement much lower - about 40% down
            arrow_part = ""
            
            if i == int(max_height * 0.4):  # Requirements line
                req_text = evolution_req.replace('\n', ' ') if evolution_req else ''
                arrow_part = f"{req_text:^40}" if req_text else " " * 40
            elif i == int(max_height * 0.4) + 1:  # Arrow line
                arrow_part = "     ══════════════════════════════►     "
            elif i == int(max_height * 0.4) + 2:  # Extra spacing
                arrow_part = "                                        "
            else:
                arrow_part = "                                        "  # 40 spaces for arrow area
            
            # Combine sprites with arrow - Layout: [90] [40] [90] = 220 chars (perfect!)
            line = f"{sprite1_part}{arrow_part}{sprite2_part}"
            
            # Center the entire line in the wide border
            line = line.center(border_width-2)
            print(f"║ {line} ║")
        
        # More spacing at the bottom
        print("║" + " " * (border_width-2) + "║")
        print("║" + " " * (border_width-2) + "║")
    
    def _display_complex_evolution_wide(self, stages: List[Dict[str, Any]], border_width: int) -> None:
        """Display complex evolution chains vertically with large sprites"""
        print("║" + " " * (border_width-2) + "║")
        complex_title = "COMPLEX EVOLUTION CHAIN"
        title_line = complex_title.center(border_width-2)
        print(f"║ {title_line} ║")
        print("║" + " " * (border_width-2) + "║")
        
        for i, stage in enumerate(stages):
            pokemon_name = stage['name'].title()
            
            # Display Pokemon name
            name_line = f"Stage {stage['stage']}: {pokemon_name}"
            name_line = name_line.center(border_width-2)
            print(f"║ {name_line} ║")
            
            # Display evolution requirement if not first stage
            if i > 0:
                req_text = self.format_evolution_requirement(stage)
                if req_text:
                    req_line = f"({req_text.replace(chr(10), ', ')})"
                    req_line = req_line.center(border_width-2)
                    print(f"║ {req_line} ║")
            
            # Display large sprite
            if stage.get('pokemon_data'):
                sprite_url = stage['pokemon_data'].get('sprites', {}).get('front_default')
                if sprite_url:
                    large_sprite = self.formatter.get_sprite_ascii(sprite_url, width=60)
                    sprite_lines = large_sprite.split('\n')
                    for line in sprite_lines[:20]:  # Limit height for complex chains
                        sprite_line = line[:60].center(border_width-2)
                        print(f"║ {sprite_line} ║")
            
            # Add arrow except for last stage
            if i < len(stages) - 1:
                arrow_line = "↓".center(border_width-2)
                print(f"║ {arrow_line} ║")
                print("║" + " " * (border_width-2) + "║")
    
    def get_evolution_chain(self, pokemon_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Main method to get complete evolution chain data"""
        try:
            # Get evolution chain data
            chain_data = self.get_evolution_chain_data(pokemon_data)
            if not chain_data:
                return None
            
            # Parse the evolution chain
            evolution_stages = self.parse_evolution_chain(chain_data)
            if not evolution_stages:
                return None
            
            # Get sprites for each stage
            enhanced_stages = self.get_pokemon_sprites(evolution_stages)
            
            return enhanced_stages
            
        except Exception as e:
            print(f"Error getting evolution chain: {e}")
            return None