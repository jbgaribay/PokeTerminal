# config.py
"""
Configuration constants for the Pokédex Terminal App
"""

# API URLs
POKEMON_BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
SPECIES_BASE_URL = "https://pokeapi.co/api/v2/pokemon-species/"

# ASCII characters for sprite rendering
ASCII_CHARS = "@@%%##**++==--::..  "

# Type colors for display
TYPE_COLORS = {
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

# Move category colors
CATEGORY_COLORS = {
    'physical': '91',  # red
    'special': '94',   # blue
    'status': '93'     # yellow
}

# Generation to version group mappings
GEN_VERSION_GROUPS = {
    1: {
        'all': ['red-blue', 'yellow'],
        'red-blue': ['red-blue'],
        'yellow': ['yellow']
    },
    2: {
        'all': ['gold-silver', 'crystal'],
        'gold-silver': ['gold-silver'],
        'crystal': ['crystal']
    },
    3: {
        'all': ['ruby-sapphire', 'emerald', 'firered-leafgreen'],
        'ruby-sapphire': ['ruby-sapphire'],
        'emerald': ['emerald'],
        'firered-leafgreen': ['firered-leafgreen']
    },
    4: {
        'all': ['diamond-pearl', 'platinum', 'heartgold-soulsilver'],
        'diamond-pearl': ['diamond-pearl'],
        'platinum': ['platinum'],
        'heartgold-soulsilver': ['heartgold-soulsilver']
    },
    5: {
        'all': ['black-white', 'black-2-white-2'],
        'black-white': ['black-white'],
        'black-2-white-2': ['black-2-white-2']
    },
    6: {
        'all': ['x-y', 'omega-ruby-alpha-sapphire'],
        'x-y': ['x-y'],
        'omega-ruby-alpha-sapphire': ['omega-ruby-alpha-sapphire']
    },
    7: {
        'all': ['sun-moon', 'ultra-sun-ultra-moon'],
        'sun-moon': ['sun-moon'],
        'ultra-sun-ultra-moon': ['ultra-sun-ultra-moon']
    },
    8: {
        'all': ['sword-shield'],
        'sword-shield': ['sword-shield']
    },
    9: {
        'all': ['scarlet-violet'],
        'scarlet-violet': ['scarlet-violet']
    }
}

# Version name to version group mapping for locations
VERSION_GROUP_MAP = {
    'red': 'red-blue', 'blue': 'red-blue', 'yellow': 'yellow',
    'gold': 'gold-silver', 'silver': 'gold-silver', 'crystal': 'crystal',
    'ruby': 'ruby-sapphire', 'sapphire': 'ruby-sapphire', 'emerald': 'emerald',
    'firered': 'firered-leafgreen', 'leafgreen': 'firered-leafgreen',
    'diamond': 'diamond-pearl', 'pearl': 'diamond-pearl', 'platinum': 'platinum',
    'heartgold': 'heartgold-soulsilver', 'soulsilver': 'heartgold-soulsilver',
    'black': 'black-white', 'white': 'black-white',
    'black-2': 'black-2-white-2', 'white-2': 'black-2-white-2',
    'x': 'x-y', 'y': 'x-y',
    'omega-ruby': 'omega-ruby-alpha-sapphire', 'alpha-sapphire': 'omega-ruby-alpha-sapphire',
    'sun': 'sun-moon', 'moon': 'sun-moon',
    'ultra-sun': 'ultra-sun-ultra-moon', 'ultra-moon': 'ultra-sun-ultra-moon',
    'sword': 'sword-shield', 'shield': 'sword-shield',
    'scarlet': 'scarlet-violet', 'violet': 'scarlet-violet'
}

# Roman numeral to number conversion for generations
ROMAN_TO_INT = {
    'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5,
    'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9
}

# Stat name mappings
STAT_NAMES = {
    'hp': 'HP',
    'attack': 'Attack',
    'defense': 'Defense',
    'special-attack': 'Sp. Atk',
    'special-defense': 'Sp. Def',
    'speed': 'Speed'
}

# Nature effects mapping
NATURES = {
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