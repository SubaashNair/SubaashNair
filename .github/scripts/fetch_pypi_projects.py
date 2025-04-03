#!/usr/bin/env python3
"""
Script to fetch PyPI package information and update the GitHub profile README.md
"""

import re
import json
import requests
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# List of PyPI packages to include
PACKAGES = [
    "outlier-cleaner",
    "optimrl",
    "stats-confidence-intervals",
    "smartpredict",
    "stopwordz"
]

def fetch_pypi_package_info(package_name):
    """Fetch package information from PyPI"""
    try:
        # Get package info from PyPI API
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url)
        response.raise_for_status()
        package_data = response.json()
        
        # Get additional information from the PyPI page to extract description
        pypi_page = requests.get(f"https://pypi.org/project/{package_name}/")
        soup = BeautifulSoup(pypi_page.text, 'html.parser')
        
        # Try to get a short description
        description = package_data.get("info", {}).get("summary", "")
        if not description and soup:
            # Try to extract description from page
            desc_element = soup.select_one("p.package-description__summary")
            if desc_element:
                description = desc_element.text.strip()
        
        return {
            "name": package_name,
            "version": package_data.get("info", {}).get("version", ""),
            "description": description,
            "url": f"https://pypi.org/project/{package_name}/"
        }
    except Exception as e:
        print(f"Error fetching info for {package_name}: {e}")
        return {
            "name": package_name,
            "version": "",
            "description": "Python package by Subashanan Nair",
            "url": f"https://pypi.org/project/{package_name}/"
        }

def update_readme(packages_info):
    """Update the README.md with package information"""
    readme_path = Path('README.md')
    if not readme_path.exists():
        print("README.md not found")
        return False
    
    readme_content = readme_path.read_text()
    
    # Create HTML table for packages (2 columns)
    table_rows = []
    for i in range(0, len(packages_info), 2):
        row = packages_info[i:i+2]
        
        if len(row) == 2:
            table_row = f"""  <tr>
    <td align="center">
      <a href="{row[0]['url']}">
        <img src="https://img.shields.io/pypi/v/{row[0]['name']}.svg" alt="PyPI version" />
        <br />
        <b>{row[0]['name']}</b>
      </a>
      <br />
      {row[0]['description']}
    </td>
    <td align="center">
      <a href="{row[1]['url']}">
        <img src="https://img.shields.io/pypi/v/{row[1]['name']}.svg" alt="PyPI version" />
        <br />
        <b>{row[1]['name']}</b>
      </a>
      <br />
      {row[1]['description']}
    </td>
  </tr>"""
        else:
            # If we have an odd number of packages, make the last one span both columns
            table_row = f"""  <tr>
    <td align="center" colspan="2">
      <a href="{row[0]['url']}">
        <img src="https://img.shields.io/pypi/v/{row[0]['name']}.svg" alt="PyPI version" />
        <br />
        <b>{row[0]['name']}</b>
      </a>
      <br />
      {row[0]['description']}
    </td>
  </tr>"""
            
        table_rows.append(table_row)
    
    table_html = f"""<table>
{chr(10).join(table_rows)}
</table>"""
    
    # Replace the PyPI packages section in the README
    pypi_section_pattern = r"## 📦 My PyPI Packages\s*<table>[\s\S]*?</table>"
    new_pypi_section = f"## 📦 My PyPI Packages\n\n{table_html}"
    
    if re.search(pypi_section_pattern, readme_content):
        updated_readme = re.sub(pypi_section_pattern, new_pypi_section, readme_content)
    else:
        # If section doesn't exist, try to add it at a logical place
        updated_readme = readme_content.replace(
            "## 🏆 Kaggle Achievements", 
            f"{new_pypi_section}\n\n## 🏆 Kaggle Achievements"
        )
    
    # Write the updated content back to the README
    readme_path.write_text(updated_readme)
    return True

def main():
    """Main function to fetch packages and update README"""
    print("Fetching PyPI package information...")
    packages_info = [fetch_pypi_package_info(package) for package in PACKAGES]
    
    # Sort packages by name
    packages_info.sort(key=lambda x: x["name"])
    
    print("Updating README.md...")
    if update_readme(packages_info):
        print("README.md updated successfully!")
    else:
        print("Failed to update README.md")

if __name__ == "__main__":
    main() 