# main.py
"""
Main entry point for the Pokédx Terminal Application
"""

import sys
from pokedex_core import PokedexCore
from move_handler import MoveHandler
from location_handler import LocationHandler
from evolution_handler import EvolutionHandler
from comparison_handler import ComparisonHandler
from route_handler import RouteHandler
from breeding_handler import BreedingHandler

class PokedexTerminal:
    """Main application class that coordinates all functionality"""
    
    def __init__(self):
        self.pokedex_core = PokedexCore()
        self.move_handler = MoveHandler()
        self.location_handler = LocationHandler()
        self.evolution_handler = EvolutionHandler()
        self.comparison_handler = ComparisonHandler()
        self.route_handler = RouteHandler()
        self.breeding_handler = BreedingHandler()
        self.current_pokemon = None
    
    def handle_comparison_command(self, query: str) -> None:
        """Handle Pokemon comparison command"""
        try:
            # Parse compare command: "compare pikachu raichu"
            parts = query.split()
            if len(parts) != 3:
                print("❌ Invalid compare format! Use: compare <pokemon1> <pokemon2>")
                print("   Example: compare pikachu raichu")
                return
            
            pokemon1_name = parts[1].lower()
            pokemon2_name = parts[2].lower()
            
            self.comparison_handler.compare_pokemon(pokemon1_name, pokemon2_name)
            
        except Exception as e:
            print(f"❌ Error comparing Pokémon: {e}")
    
    def print_help_commands(self) -> None:
        """Display all available commands"""
        print("""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                POKÉDEX COMMANDS                                                    ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                 ║
║ BASIC COMMANDS:                                                                                                 ║
║ • 'help' or 'c' - Show this command list                                                                       ║
║ • 'exit' or 'quit' - Exit the Pokédex                                                                          ║
║ • 'games' - Show available game versions                                                                       ║
║                                                                                                                 ║
║ SEARCH COMMANDS:                                                                                                ║
║ • Type any Pokémon name to search (e.g., 'pikachu', 'charizard')                                              ║
║ • Numbers work too (e.g., '25' for Pikachu)                                                                    ║
║                                                                                                                 ║
║ COMPARISON COMMANDS:                                                                                            ║
║ • 'compare <pokemon1> <pokemon2>' - Compare two Pokémon side by side                                           ║
║   Example: 'compare pikachu raichu'                                                                            ║
║                                                                                                                 ║
║ ROUTE/LOCATION COMMANDS:                                                                                        ║
║ • 'route <number> [game]' - Show Pokemon found at a specific route                                             ║
║ • '<location> [game]' - Show Pokemon found at a specific location                                              ║
║   Examples: 'route 104', 'route 104 emerald', 'victory road platinum'                                         ║
║                                                                                                                 ║
║ COMMANDS AFTER VIEWING A POKÉMON:                                                                              ║
║ • 'moves gen X [game]' - Show all moves for generation X (optionally specific game)                          ║
║ • 'learnset gen X [game]' - Show only level-up moves                                                          ║
║ • 'tm gen X [game]' - Show only TM/HM moves                                                                   ║
║ • 'egg gen X [game]' - Show only egg moves                                                                    ║
║ • 'tutor gen X [game]' - Show only move tutor moves                                                           ║
║ • 'location gen X [game]' - Show encounter locations for generation/game                                      ║
║ • 'location <game>' - Show encounter locations for specific game                                              ║
║ • 'evo' - Show evolution chain with ASCII sprites
 ║ • 'breed <pokemon1> <pokemon2>' - Check breeding compatibility and egg move potential                          ║
║                                                                             ║
║                                                                       ║
║ EXAMPLES:                                                                                                       ║
║ • 'tm gen 3' - All Gen 3 TM moves                                                                             ║
║ • 'tm gen 3 emerald' - Only Emerald TM moves                                                                  ║
║ • 'tutor gen 7 ultra-sun-ultra-moon' - Move tutor moves from Ultra Sun/Moon                                  ║
║ • 'location gen 4 platinum' - Where to find this Pokémon in Platinum                                         ║
║ • 'location emerald' - Where to find this Pokémon in Emerald                                                 ║
║ • 'evo' - See the complete evolution chain                                                                    ║
║ • 'compare bulbasaur venusaur' - Compare starter with its final evolution                                     ║
║                                                                                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
        """)
    
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
        """Process user command and return True to continue, False to exit"""
        query = query.strip()
        
        if not query:
            return True
        
        # Convert to lowercase for command checking
        query_lower = query.lower()
        
        print(f"DEBUG: Processing '{query}' (lower: '{query_lower}')")  # DEBUG LINE
        
        # === SPECIAL COMMANDS (check these FIRST with immediate returns) ===
        
        # Help commands
        if query_lower == 'help' or query_lower == 'c':
            print("DEBUG: Help command detected!")  # DEBUG LINE
            self.print_help_commands()
            return True
        
        # Exit commands
        if query_lower == 'exit' or query_lower == 'quit':
            print("DEBUG: Exit command detected!")  # DEBUG LINE
            print("👋 Thanks for using the Pokédex Terminal! Gotta catch 'em all!")
            return False
        
        # Games list
        if query_lower == 'games':
            print("DEBUG: Games command detected!")  # DEBUG LINE
            self.print_available_games()
            return True
        
        # Pokemon comparison - check this carefully
        if query_lower.startswith('compare '):
            print("DEBUG: Compare command detected!")  # DEBUG LINE
            self.handle_comparison_command(query)
            return True
        
        if query_lower.startswith('breed'):
            print("DEBUG: Breed command detected!") # DEBUG LINE
            self.breeding_handler.handle_breeding_command(query)
            return True

        # Route/Location Pokemon lookup
        if query_lower.startswith('route ') or any(query_lower.startswith(loc) for loc in ['victory road', 'safari zone', 'viridian forest', 'mount silver']):
            print("DEBUG: Route command detected!")  # DEBUG LINE
            self.route_handler.handle_route_query(query)
            return True
        
        # === COMMANDS THAT NEED CURRENT POKEMON ===
        
        # Evolution chain
        if query_lower == 'evo':
            print("DEBUG: Evo command detected!")  # DEBUG LINE
            if not self.current_pokemon:
                print("❌ Please search for a Pokémon first before viewing evolution chain!")
            else:
                self.handle_evolution_command(self.current_pokemon)
            return True
        
        # Move-related commands
        if (query_lower.startswith('moves gen') or 
            query_lower.startswith('learnset gen') or 
            query_lower.startswith('tm gen') or 
            query_lower.startswith('egg gen') or 
            query_lower.startswith('tutor gen')):
            print("DEBUG: Move command detected!")  # DEBUG LINE
            if not self.current_pokemon:
                print("❌ Please search for a Pokémon first before viewing moves!")
            else:
                self.handle_move_command(query, self.current_pokemon)
            return True
        
        # Location command - FIXED to handle both formats
        if (query_lower.startswith('location gen') or 
            (query_lower.startswith('location ') and not query_lower.startswith('location gen'))):
            print("DEBUG: Location command detected!")  # DEBUG LINE
            if not self.current_pokemon:
                print("❌ Please search for a Pokémon first before viewing locations!")
            else:
                self.handle_location_command(query, self.current_pokemon)
            return True
        
        # === POKEMON SEARCH (only if no commands matched above) ===
        print(f"DEBUG: No command matched, searching for Pokemon: {query}")  # DEBUG LINE
        print(f"🔍 Searching for: {query}")
        result = self.pokedex_core.search_pokemon(query)
        if result:
            self.current_pokemon = result
        
        return True
    
    def handle_move_command(self, query: str, pokemon_data: dict) -> None:
        """Handle move-related commands"""
        try:
            self.move_handler.handle_move_query(query, pokemon_data)
        except Exception as e:
            print(f"❌ Error loading move data: {e}")
    
    def handle_location_command(self, query: str, pokemon_data: dict) -> None:
        """Handle location command"""
        try:
            self.location_handler.handle_location_query(query, pokemon_data)
        except Exception as e:
            print(f"❌ Error loading location data: {e}")
    
    def print_available_games(self) -> None:
        """Print available game versions"""
        print("""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                            AVAILABLE GAME VERSIONS                                               ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                 ║
║ GENERATION 1: red, blue, yellow                                                                                ║
║ GENERATION 2: gold, silver, crystal                                                                            ║
║ GENERATION 3: ruby, sapphire, emerald, firered, leafgreen                                                     ║
║ GENERATION 4: diamond, pearl, platinum, heartgold, soulsilver                                                 ║
║ GENERATION 5: black, white, black-2, white-2                                                                  ║
║ GENERATION 6: x, y, omega-ruby, alpha-sapphire                                                                ║
║ GENERATION 7: sun, moon, ultra-sun, ultra-moon                                                                ║
║ GENERATION 8: sword, shield                                                                                    ║
║ GENERATION 9: scarlet, violet                                                                                  ║
║                                                                                                                 ║
║ Usage: 'moves gen 3 emerald' or 'tm gen 4 platinum'                                                           ║
║                                                                                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
        """)
    
    def print_welcome_message(self):
        """Display the welcome message and basic commands"""
        print("""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                               POKÉDEX TERMINAL                                                    ║
║                                            Welcome, Trainer! 🎮                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                 ║
║ 🔍 QUICK START:                                                                                                 ║
║ • Type any Pokémon name to search (e.g., 'pikachu')                                                            ║
║ • Type 'help' or 'c' to see all commands                                                                       ║
║ • Type 'compare pikachu raichu' to compare Pokémon                                                             ║
║ • Type 'exit' to quit                                                                                          ║
║                                                                                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
        """)
    
    def run(self):
        """Main application loop"""
        self.print_welcome_message()
        
        while True:
            try:
                query = input("\n🔍 Enter Pokémon name/ID or command (current: {current}): ".format(
                    current=self.current_pokemon['name'].title() if self.current_pokemon else "None"
                ))
                
                # Process the command/query
                if not self.process_command(query):
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using the Pokédx Terminal!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again!")

if __name__ == "__main__":
    app = PokedexTerminal()
    app.run()