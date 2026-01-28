# ===========================================================================
# DATASET AUTO-NAMING UTILITY
# ===========================================================================
# Automatically generates clean dataset names from search queries
# For use in client data exports

def generate_dataset_name(search_query: str, platform: str = "google_maps") -> str:
    """
    Converts a search query into a clean dataset name.
    
    Examples:
        "roofing companies in Austin TX" → "Roofers - Austin TX"
        "marketing agencies near me in NYC" → "Marketing Agencies - NYC"
        "dentists California" → "Dentists - California"
    
    Args:
        search_query: The original search query
        platform: The platform used (for context)
    
    Returns:
        str: Clean dataset name in format "[Industry] - [Location]"
    """
    import re
    
    query = search_query.lower().strip()
    
    # Remove common filler words
    query = re.sub(r'\b(near me|in|the|a|an|top|best|list of)\b', '', query)
    query = ' '.join(query.split())  # Clean multiple spaces
    
    # Extract location indicators
    locations = []
    location_patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s+[A-Z]{2})',  # "Austin TX", "New York NY"
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "California", "New York"
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, search_query)  # Use original query for proper capitals
        if matches:
            locations.extend(matches)
            break
    
    location = locations[0] if locations else "USA"
    
    # Extract industry/category
    industry_map = {
        'roof': 'Roofers',
        'marketing': 'Marketing Agencies',
        'agency': 'Agencies',
        'dental': 'Dentists',
        'dentist': 'Dentists',
        'plumb': 'Plumbers',
        'hvac': 'HVAC Companies',
        'startup': 'Startups',
        'software': 'Software Companies',
        'saas': 'SaaS Companies',
        'ecommerce': 'E-commerce Brands',
        'brand': 'Brands',
        'restaurant': 'Restaurants',
        'cafe': 'Cafes',
        'law': 'Law Firms',
        'attorney': 'Attorneys',
        'real estate': 'Real Estate Agencies',
        'contractor': 'Contractors',
        'construction': 'Construction Companies',
        'consultant': 'Consultants',
        'agency': 'Agencies',
    }
    
    industry = "Companies"  # default
    for key, value in industry_map.items():
        if key in query:
            industry = value
            break
    
    # Generate dataset name
    dataset_name = f"{industry} - {location}"
    
    return dataset_name


def generate_tags(search_query: str, industry: str) -> list:
    """
    Generates filter tags from the search query.
    
    Args:
        search_query: The original search query
        industry: Detected industry category
    
    Returns:
        list: Array of tags for filtering
    """
    tags = []
    
    # Add industry tag
    if industry:
        tags.append(industry.lower().replace(' - ', '-'))
    
    # Add location tags
    import re
    state_matches = re.findall(r'\b([A-Z]{2})\b', search_query)
    if state_matches:
        tags.append(state_matches[0].lower())
    
    # Add business type category
    if any(word in search_query.lower() for word in ['roofer', 'plumber', 'hvac', 'contractor']):
        tags.append('home-services')
    elif any(word in search_query.lower() for word in ['marketing', 'agency', 'consulting']):
        tags.append('b2b-services')
    elif any(word in search_query.lower() for word in ['startup', 'software', 'saas']):
        tags.append('tech')
    elif any(word in search_query.lower() for word in ['restaurant', 'cafe', 'food']):
        tags.append('food-hospitality')
    
    return tags


# ===========================================================================
# USAGE EXAMPLE
# ===========================================================================
if __name__ == "__main__":
    # Test cases
    test_queries = [
        "roofing companies in Austin TX",
        "marketing agencies near me in New York",
        "dentists California",
        "SaaS startups in San Francisco",
        "HVAC contractors Dallas Texas",
    ]
    
    for query in test_queries:
        dataset_name = generate_dataset_name(query)
        tags = generate_tags(query, dataset_name.split(' - ')[0])
        print(f"Query: {query}")
        print(f"  → Dataset: {dataset_name}")
        print(f"  → Tags: {tags}")
        print()
