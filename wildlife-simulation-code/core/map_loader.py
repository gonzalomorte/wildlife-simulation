import json
import os

def load_maps():
    """
    Load all maps from the maps.json file.
    
    Returns:
        dict: Dictionary containing all map configurations
    """
    maps_path = os.path.join(os.path.dirname(__file__), '..', 'maps', 'maps.json')
    
    with open(maps_path, 'r') as f:
        data = json.load(f)
    
    return data['maps']


def get_map(map_index):
    """
    Get a specific map by its index.
    
    Args:
        map_index (int): The index of the map to retrieve (0-9)
    
    Returns:
        dict: The map configuration, or None if index is invalid
    """
    maps = load_maps()
    
    for map_data in maps:
        if map_data['id'] == map_index:
            return map_data
    
    return None


def list_available_maps():
    """
    Get a list of all available maps with their basic info.
    
    Returns:
        list: List of tuples (id, name, description)
    """
    maps = load_maps()
    return [(m['id'], m['name'], m['description']) for m in maps]
