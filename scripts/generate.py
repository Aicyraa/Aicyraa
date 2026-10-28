"""Refresh public GitHub data and regenerate the profile artwork."""
import json
import os
import sys
from fetch_data import fetch_github_data
from refresh_avatar import refresh_avatar
from profile_design import ROOT, render_all


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else 'Aicyraa'
    token = os.environ.get('GH_PAT') or os.environ.get('GITHUB_TOKEN')
    path = ROOT / 'scripts/data.json'
    data = fetch_github_data(username, token)
    if data:
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    elif path.exists():
        print('Using the last successful snapshot.')
        data = json.loads(path.read_text())
    else:
        raise SystemExit('No fresh or saved profile data available.')
    refresh_avatar(username, token)
    render_all(data)
    print('Generated profile panel, tools, streaks, and language graphics.')


if __name__ == '__main__':
    main()
