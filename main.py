#!/usr/bin/env python3
"""
Pokédex Terminal App - Main Entry Point
A modular command-line Pokédex that fetches data from PokéAPI
"""

import sys
from pokedex_core import PokedexCore
from move_handler import MoveHandler
from location_handler import LocationHandler
from evolution_handler import EvolutionHandler

class PokedexTerminal:
    """Main application class that coordinates all functionality"""
    
    def __init__(self):
        self.pokedex_core = PokedexCore()
        self.move_handler = MoveHandler()
        self.location_handler = LocationHandler()
        self.evolution_handler = EvolutionHandler()
        self.current_pokemon = None
    
    def print_available_games(self):
        """Print available game options for each generation"""
        print("""
Available games for specific learnsets and locations:
Generation 1: red-blue, yellow
Generation 2: gold-silver, crystal  
Generation 3: ruby-sapphire, emerald, firered-leafgreen
Generation 4: diamond-pearl, platinum, heartgold-soulsilver
Generation 5: black-white, black-2-white-2
Generation 6: x-y, omega-ruby-alpha-sapphire
Generation 7: sun-moon, ultra-sun-ultra-moon
Generation 8: sword-shield
Generation 9: scarlet-violet

Examples: 'tm gen 3 emerald', 'location gen 4 platinum'
        """)
    
    def handle_move_command(self, command_type: str, generation: int, specific_game: str, pokemon_data: dict) -> None:
        """Handle move-related commands"""
        try:
            # Display loading message for moves
            if specific_game:
                print(f"\n🔍 Loading {specific_game.replace('-', ' ').title()} {command_type} for {pokemon_data['name'].title()}...")
            else:
                print(f"\n🔍 Loading Generation {generation} {command_type} for {pokemon_data['name'].title()}...")
            
            moves_data = self.move_handler.get_learnset_data(pokemon_data, generation, specific_game)
            
            if moves_data:
                self.move_handler.display_specific_moves(pokemon_data['name'], generation, command_type, moves_data)
            else:
                print("❌ Could not load move data.")
        except Exception as e:
            print(f"❌ Error loading move data: {e}")
    
    def handle_location_command(self, generation: int, specific_game: str, pokemon_data: dict) -> None:
        """Handle location-related commands"""
        try:
            # Display loading message for location
            if specific_game:
                print(f"\n🔍 Loading {specific_game.replace('-', ' ').title()} locations for {pokemon_data['name'].title()}...")
            else:
                print(f"\n🔍 Loading Generation {generation} locations for {pokemon_data['name'].title()}...")
            
            location_data = self.location_handler.get_location_data(pokemon_data, generation, specific_game)
            
            if location_data:
                self.location_handler.display_locations(pokemon_data['name'], generation, location_data)
            else:
                print("❌ Could not load location data.")
        except Exception as e:
            print(f"❌ Error loading location data: {e}")
    
    def handle_evolution_command(self, pokemon_data: dict) -> None:
        """Handle evolution command"""
        try:
            print(f"\n🔍 Loading evolution chain for {pokemon_data['name'].title()}...")
            
            evolution_stages = self.evolution_handler.get_evolution_chain(pokemon_data)
            
            if evolution_stages:
                self.evolution_handler.display_evolution_chain(pokemon_data['name'], evolution_stages)
            else:
                print("❌ Could not load evolution data.")
        except Exception as e:
            print(f"❌ Error loading evolution data: {e}")
    
    def process_command(self, query: str) -> bool:
        """Process user commands. Returns True if command was handled, False if it's a Pokemon search"""
        # Check for special commands first
        if query.lower() in ['quit', 'exit', 'q']:
            print("\nThanks for using Pokédx Terminal! Goodbye! 👋")
            return True
        
        if query.lower() == 'games':
            self.print_available_games()
            return True
        
        if query.lower() == 'evo':
            if not self.current_pokemon:
                print("❌ Please search for a Pokémon first before viewing evolution chain!")
                return True
            self.handle_evolution_command(self.current_pokemon)
            return True
        
        if not query:
            print("Please enter a Pokémon name, ID, or command.")
            return True
        
        # Check for move and location commands
        move_commands = ['moves gen', 'learnset gen', 'tm gen', 'egg gen', 'tutor gen']
        location_commands = ['location gen']
        all_commands = move_commands + location_commands
        
        if any(query.lower().startswith(cmd) for cmd in all_commands):
            if not self.current_pokemon:
                print("❌ Please search for a Pokémon first before viewing moves or locations!")
                return True
            
            try:
                # Parse the command - supports: "command gen X" or "command gen X game"
                parts = query.lower().split()
                if len(parts) >= 3 and parts[1] == 'gen':
                    command_type = parts[0]
                    generation = int(parts[2])
                    specific_game = parts[3] if len(parts) > 3 else None
                    
                    if generation < 1 or generation > 9:
                        print("❌ Please specify a generation between 1-9")
                        return True
                    
                    # Handle location command differently from move commands
                    if command_type == 'location':
                        self.handle_location_command(generation, specific_game, self.current_pokemon)
                    else:
                        self.handle_move_command(command_type, generation, specific_game, self.current_pokemon)
                else:
                    print("❌ Invalid format. Use 'command gen X [game]' (e.g., 'tm gen 3 emerald', 'location gen 4 platinum')")
                    self.print_available_games()
                    
            except ValueError:
                print("❌ Invalid generation number")
            except Exception as e:
                print(f"❌ Error processing command: {e}")
            
            return True
        
        # If we get here, it's not a special command
        return False
    
    def run(self):
        """Main application loop"""
        print("""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                              POKÉDEX TERMINAL                                ║
║                         Gotta catch 'em all!                                  ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════╝

Welcome to the Pokédex Terminal!
Search for any Pokémon by name or ID number.

MOVE COMMANDS (after viewing a Pokémon):
• 'moves gen X [game]' - Show all moves for generation X (optionally specific game)
• 'learnset gen X [game]' - Show only level-up moves
• 'tm gen X [game]' - Show only TM/HM moves  
• 'egg gen X [game]' - Show only egg moves
• 'tutor gen X [game]' - Show only move tutor moves
• 'location gen X [game]' - Show encounter locations for generation/game
• 'evo' - Show evolution chain with ASCII sprites

EXAMPLES:
• 'tm gen 3' - All Gen 3 TM moves
• 'tm gen 3 emerald' - Only Emerald TM moves
• 'tutor gen 7 ultra-sun-ultra-moon' - Move tutor moves from Ultra Sun/Moon
• 'location gen 4 platinum' - Where to find this Pokémon in Platinum
• 'evo' - See the complete evolution chain

Type 'games' to see available game options for each generation.
Type 'quit' or 'exit' to close the application.

        """)

        while True:
            try:
                if self.current_pokemon:
                    query = input(f"\n🔍 Enter Pokémon name/ID or command (current: {self.current_pokemon['name'].title()}): ").strip()
                else:
                    query = input("\n🔍 Enter Pokémon name or ID: ").strip()

                # Process command and check if it was handled
                command_handled = self.process_command(query)
                if command_handled:
                    continue
                
                # If not a command, treat as Pokemon search
                print(f"\n🔍 Searching for: {query}")
                print("Loading...")

                data = self.pokedex_core.get_pokemon_data(query)

                if data is None:
                    print(f"\n❌ Pokemon '{query}' not found!")
                    print("Try searching by name (e.g., 'pikachu') or ID number (e.g., '25')")
                    self.current_pokemon = None
                    continue

                self.pokedex_core.display_pokemon(data)
                self.current_pokemon = data['pokemon']  # Store current pokemon for move/location commands

            except KeyboardInterrupt:
                print("\n\nThanks for using Pokédex Terminal! Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.")

def main():
    """Entry point of the application"""
    try:
        app = PokedexTerminal()
        app.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)

if __name__ == "__main__":
    main()