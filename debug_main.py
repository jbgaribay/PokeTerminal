# debug_main.py - Simple test version to debug the command issue

def test_process_command(query):
    """Test function to see if command detection works"""
    query = query.strip()
    query_lower = query.lower()
    
    print(f"Testing query: '{query}'")
    print(f"Query lower: '{query_lower}'")
    
    # Test help command
    if query_lower == 'help' or query_lower == 'c':
        print("✅ HELP command detected!")
        return True
    
    # Test compare command
    if query_lower.startswith('compare '):
        print("✅ COMPARE command detected!")
        return True
    
    # Test exit command
    if query_lower == 'exit' or query_lower == 'quit':
        print("✅ EXIT command detected!")
        return False
    
    print("❌ No command detected - would search for Pokemon")
    return True

# Test the commands
if __name__ == "__main__":
    print("=== TESTING COMMAND DETECTION ===")
    
    test_queries = ["help", "c", "compare pikachu raichu", "exit", "pikachu"]
    
    for query in test_queries:
        print(f"\n--- Testing: '{query}' ---")
        result = test_process_command(query)
        print(f"Continue: {result}")
        print()