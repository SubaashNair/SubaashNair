#!/usr/bin/env python3
"""
Script to fetch Kaggle stats and update the GitHub profile README.md
"""

import re
import os
import json
import requests
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

def authenticate_kaggle():
    """Authenticate with Kaggle API"""
    try:
        api = KaggleApi()
        api.authenticate()
        return api
    except Exception as e:
        print(f"Error authenticating with Kaggle: {e}")
        return None

def get_kaggle_stats(username):
    """Get Kaggle stats for a user"""
    try:
        # First try using Kaggle API
        api = authenticate_kaggle()
        if api:
            # Get user profile
            user = api.user_profile(username)
            return {
                "username": username,
                "name": user.displayName,
                "tier": user.tier,
                "medals_count": user.medalsCount,
                "competitions_count": len(api.competitions_list_with_user(username)),
                "datasets_count": len(api.dataset_list_with_user(username)),
                "notebooks_count": len(api.kernels_list_with_user(username)),
                "url": f"https://www.kaggle.com/{username}"
            }
        else:
            # Fallback: Use web scraping
            url = f"https://www.kaggle.com/{username}"
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # Basic information even if we can't get detailed stats
            return {
                "username": username,
                "name": username,
                "tier": "Unknown",
                "url": url
            }
    except Exception as e:
        print(f"Error fetching Kaggle stats: {e}")
        return {
            "username": username,
            "name": username,
            "tier": "Unknown",
            "url": f"https://www.kaggle.com/{username}"
        }

def update_readme(kaggle_stats):
    """Update the README.md with Kaggle stats"""
    readme_path = Path('README.md')
    if not readme_path.exists():
        print("README.md not found")
        return False
    
    readme_content = readme_path.read_text()
    
    # Create Kaggle stats section
    stats_html = f"""[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=Kaggle&logoColor=white)](https://www.kaggle.com/{kaggle_stats['username']})

<table>
  <tr>
    <td>Tier</td>
    <td><b>{kaggle_stats.get('tier', 'Unknown')}</b></td>
  </tr>"""
    
    # Add medals if available
    if 'medals_count' in kaggle_stats:
        stats_html += f"""
  <tr>
    <td>Medals</td>
    <td><b>{kaggle_stats['medals_count']}</b></td>
  </tr>"""
    
    # Add competitions if available
    if 'competitions_count' in kaggle_stats:
        stats_html += f"""
  <tr>
    <td>Competitions</td>
    <td><b>{kaggle_stats['competitions_count']}</b></td>
  </tr>"""
    
    # Add datasets if available
    if 'datasets_count' in kaggle_stats:
        stats_html += f"""
  <tr>
    <td>Datasets</td>
    <td><b>{kaggle_stats['datasets_count']}</b></td>
  </tr>"""
    
    # Add notebooks if available
    if 'notebooks_count' in kaggle_stats:
        stats_html += f"""
  <tr>
    <td>Notebooks</td>
    <td><b>{kaggle_stats['notebooks_count']}</b></td>
  </tr>"""
    
    # Close the table
    stats_html += """
</table>"""
    
    # Replace the Kaggle section in the README
    kaggle_section_pattern = r"## 🏆 Kaggle Achievements\s*\n\[\!\[Kaggle\].*?\n\n.*?(<!--|$)"
    new_kaggle_section = f"## 🏆 Kaggle Achievements\n\n{stats_html}\n\n"
    
    if re.search(kaggle_section_pattern, readme_content):
        updated_readme = re.sub(kaggle_section_pattern, new_kaggle_section, readme_content)
    else:
        # If section doesn't exist, try to find where to add it
        if "## 📦 My PyPI Packages" in readme_content:
            updated_readme = readme_content.replace(
                "## 📦 My PyPI Packages",
                f"{new_kaggle_section}## 📦 My PyPI Packages"
            )
        else:
            # Add after "About Me" section
            updated_readme = readme_content.replace(
                "## 🔭 About Me",
                f"## 🔭 About Me\n\n{new_kaggle_section}"
            )
    
    # Write the updated content back to the README
    readme_path.write_text(updated_readme)
    return True

def main():
    """Main function to fetch Kaggle stats and update README"""
    print("Fetching Kaggle stats...")
    
    # Get Kaggle username from environment or default to 'noir1112'
    kaggle_username = os.environ.get('KAGGLE_USERNAME', 'noir1112')
    
    # Fetch stats
    kaggle_stats = get_kaggle_stats(kaggle_username)
    
    print("Updating README.md...")
    if update_readme(kaggle_stats):
        print("README.md updated successfully!")
    else:
        print("Failed to update README.md")

if __name__ == "__main__":
    main() 