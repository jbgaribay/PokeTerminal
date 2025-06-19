# Pokédex Terminal App 

Command-line Pokédex application that fetches data from the PokéAPI and displays Pokémon information.

## Features 

- **Pokémon Information**: Search by name or ID to get detailed stats, abilities, types, and descriptions
- **Stats**: View base stats with visual bar representations
- **Abilities **: Get details of each Pokémon's abilities
- **Nature Recommendations**: Automatically show optimal natures based on stat distribution
- **Breeding Information**: Egg groups and growth rate data

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Required Dependencies

```bash
pip install requests pillow
```

### Installation Steps

1. **Clone or download** the repository:
   ```bash
   git clone <repository-url>
   cd pokedex-terminal
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install requests pillow
   ```

3. **Make the script executable** (Linux/macOS):
   ```bash
   chmod +x pokedex.py
   ```

## Usage 

### Running the Application

```bash
python3 main.py
```

Or if made executable:
```bash
./pokedex.py
```

### Search Commands

- **By Name**: `pikachu`, `charizard`, `mewtwo`
- **By ID**: `1`, `25`, `150`
- **Case Insensitive**: `PIKACHU`, `Charizard`, `mEwTwO`

### Example Searches

```
🔍 Enter Pokémon name or ID: pikachu
🔍 Enter Pokémon name or ID: 150
🔍 Enter Pokémon name or ID: dragonite
```

### Exiting the Application

Type any of the following to exit:
- `quit`
- `exit`
- `q`
- `Ctrl+C`

## Features

### ASCII Art Generation
The app converts official Pokémon sprites into ASCII art using brightness mapping, creating unique visual representations for each Pokémon in your terminal.

### Comprehensive Data Display
- **Basic Info**: Height, weight, types with color coding
- **Battle Stats**: Base stats with visual bar representations
- **Abilities**: Detailed descriptions of all abilities
- **Breeding Info**: Egg groups and growth rates
- **Pokédex Entries**: Official flavor text descriptions

### Color-Coded Types
Each Pokémon type is displayed with appropriate colors:
- Fire (Red)
- Water (Blue)  
- Electric (Yellow)
- Grass (Green)


## Technical Details

### Dependencies

- **requests**: For API calls to PokéAPI
- **Pillow (PIL)**: For image processing and ASCII art generation
- **json**: For data parsing (built-in)
- **sys**: For system operations (built-in)
- **typing**: For type hints (built-in)
- **io**: For image handling (built-in)

### API Usage

This application uses the free [PokéAPI](https://pokeapi.co/) service to fetch Pokémon data. (No API key required)

### Performance Notes

- Images are processed in memory for ASCII conversion
- API responses are cached during the session for better performance
- Sprite ASCII generation may take a moment for the first load

## Troubleshooting 🔧

### Common Issues

**"Module not found" errors:**
```bash
pip install requests pillow
```

**"Permission denied" (Linux/macOS):**
```bash
chmod +x pokedex.py
```

**Network connection issues:**
- Ensure you have an active internet connection
- The app requires access to pokeapi.co

**ASCII art not displaying correctly:**
- Ensure your terminal supports Unicode characters
- Try adjusting your terminal's font size for better ASCII art display

### Error Messages

- **"Pokemon 'xyz' not found!"**: Check spelling or try the Pokémon's ID number
- **"Failed to load sprite"**: Network issue with image download
- **"No description available"**: Some Pokémon may have limited data

## Contributing 

Contributions are welcome! Areas for improvement:

- Add more detailed move information
- Add support for different Pokémon forms
- Improve ASCII art quality
- Add caching for offline usage
- Support for multiple languages


This project is open source. Please respect the PokéAPI's terms of service when using this application.

## Acknowledgments 🙏

- [PokéAPI](https://pokeapi.co/) for providing comprehensive Pokémon data
- The Pokémon Company

---
�
