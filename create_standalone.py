#!/usr/bin/env python3
"""
Create standalone HTML file with embedded data
"""

import json


def create_standalone_html():
    """Create a standalone HTML file with embedded JSON data."""
    # Read the original HTML
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Read the data
    with open('data.json', 'r', encoding='utf-8') as f:
        data_content = f.read()
    
    # Replace the data loading section
    old_load_section = '''        // Load data and initialize chart
        async function loadData() {
            try {
                const response = await fetch('data.json');
                const data = await response.json();'''
    
    new_load_section = f'''        // Load data and initialize chart
        async function loadData() {{
            try {{
                // Embedded data (no external file needed)
                const data = {data_content};'''
    
    # Replace in HTML
    html_content = html_content.replace(old_load_section, new_load_section)
    
    # Add a comment at the top to indicate this is standalone version
    standalone_comment = '''<!-- 
    AI Model Size vs. Release Year Analysis - Standalone Version
    This file contains embedded data and does not require external dependencies.
    Generated from index.html + data.json
-->
'''
    
    # Insert comment after DOCTYPE
    html_content = html_content.replace(
        '<!DOCTYPE html>',
        f'<!DOCTYPE html>\n{standalone_comment}'
    )
    
    # Write standalone HTML
    with open('index_standalone.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Standalone HTML created successfully!")
    print("📄 File: index_standalone.html")
    print("🎯 This file is completely self-contained and ready for deployment")
    
    # Calculate file sizes
    import os
    original_size = os.path.getsize('index.html')
    data_size = os.path.getsize('data.json')
    standalone_size = os.path.getsize('index_standalone.html')
    
    print(f"\n📊 File Sizes:")
    print(f"   Original HTML: {original_size:,} bytes")
    print(f"   Data JSON: {data_size:,} bytes")
    print(f"   Standalone HTML: {standalone_size:,} bytes")


if __name__ == "__main__":
    create_standalone_html() 