import os
import sys
import json
from fetch_data import fetch_github_data
from generate_stats import generate_stats_svg
from generate_streak import generate_streak_svg
from generate_langs import generate_langs_svg
from profile_design import finish_svg, write_static

def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "Aicyraa"
    token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    data_path = os.path.join(script_dir, "data.json")
    
    print(f"--- Refreshing Profile Graphics for {username} ---")
    data = fetch_github_data(username, token)
    
    if data:
        # Only overwrite data.json when we actually got real data
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("[OK] data.json updated with fresh data")
    elif os.path.exists(data_path):
        # Fetch failed entirely — preserve existing data.json
        print("Warning: Could not fetch fresh data. Using existing data.json...")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("Error: Could not fetch data and no existing data.json found.")
        sys.exit(1)
        
    write_static()

    # 1. Generate stats.svg
    stats_svg = generate_stats_svg(data)
    with open(os.path.join(repo_dir, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(finish_svg(stats_svg))
    print("[OK] stats.svg generated")
    
    # 2. Generate streak.svg
    streak_svg = generate_streak_svg(data)
    with open(os.path.join(repo_dir, "streak.svg"), "w", encoding="utf-8") as f:
        f.write(finish_svg(streak_svg))
    print("[OK] streak.svg generated")
    
    # 3. Generate langs.svg
    langs_svg = generate_langs_svg(data)
    with open(os.path.join(repo_dir, "langs.svg"), "w", encoding="utf-8") as f:
        f.write(finish_svg(langs_svg))
    print("[OK] langs.svg generated")
    
    print("All profile SVGs generated successfully!")

if __name__ == "__main__":
    main()
