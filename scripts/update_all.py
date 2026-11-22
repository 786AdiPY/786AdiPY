"""
update_all.py
Master automation script that regenerates all retro newsprint profile assets:
- banner.svg
- card-*.svg (Kompress, RangeShield-AI, Arize, LeetGeek)
- contributions.svg
- avatar-halftone.png
- footer.svg
- header.svg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from generate_banner import generate_banner
from generate_cards import generate_all_cards
from generate_contributions import generate_contributions
from generate_avatar import generate_avatar
from generate_footer import generate_footer
from generate_header import generate_header

def main():
    username = os.environ.get("GITHUB_ACTOR") or "786AdiPY"
    print(f"=== Regenerating Retro Newsprint Profile Assets for @{username} ===")
    
    print("\n1. Generating Banner SVG...")
    generate_banner()
    
    print("\n2. Generating Pinned Card SVGs...")
    generate_all_cards(username=username)
    
    print("\n3. Generating Contribution Calendar SVG...")
    generate_contributions(username=username)
    
    print("\n4. Generating Halftone Avatar...")
    generate_avatar(username=username)
    
    print("\n5. Generating Footer Divider SVG...")
    generate_footer()
    
    print("\n6. Generating Header Block SVG...")
    generate_header()
    
    print("\n=== All Profile Assets Successfully Updated! ===")

if __name__ == "__main__":
    main()
