"""Public GitHub statistics. Preserve the previous snapshot on fetch failures."""
import json
import os
import re
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dates, self.counts, self.levels, self.tooltip = {}, {}, {}, None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'data-date' in attrs:
            self.dates[attrs['id']] = attrs['data-date']
            self.levels[attrs['id']] = int(attrs.get('data-level', 0))
        if tag == 'tool-tip':
            self.tooltip = attrs.get('for')

    def handle_data(self, text):
        if self.tooltip:
            match = re.match(r'\s*(No|[\d,]+) contributions? on ', text)
            if match:
                self.counts[self.tooltip] = 0 if match[1] == 'No' else int(match[1].replace(',', ''))

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tooltip = None


def fetch_github_data(username, token=None):
    token = token or os.environ.get('GH_PAT') or os.environ.get('GITHUB_TOKEN')

    def request(url, payload=None):
        headers = {'User-Agent': 'Aicyraa-profile'}
        if token and url.startswith('https://api.github.com/'):
            headers['Authorization'] = f'Bearer {token}'
        if payload:
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode() if payload else None)
        with urllib.request.urlopen(req, timeout=30) as response:
            text = response.read().decode()
        return json.loads(text) if url.startswith('https://api.github.com/') else text

    try:
        calendar = CalendarParser()
        calendar.feed(request(f'https://github.com/users/{username}/contributions'))
        if not calendar.dates or set(calendar.dates) - set(calendar.counts):
            raise ValueError('Incomplete contribution calendar')
        today = datetime.now(timezone.utc).date()
        daily = {date.fromisoformat(day): calendar.counts[key] for key, day in calendar.dates.items()
                 if date.fromisoformat(day) <= today}
        days = sorted(daily)
        levels = {day: calendar.levels[key] for key, day in calendar.dates.items()}
        daily_contributions = [{'date': day.isoformat(), 'count': daily[day],
                                'level': levels[day.isoformat()]} for day in days]
        weekly = defaultdict(int)
        for day in days:
            weekly[day - timedelta(days=(day.weekday() + 1) % 7)] += daily[day]
        labels, last_month = [], None
        for i, sunday in enumerate(weekly):
            if sunday.month != last_month:
                labels.append({'index': i, 'month': sunday.strftime('%b')})
                last_month = sunday.month
        longest = run = 0
        for day in days:
            run = run + 1 if daily[day] else 0
            longest = max(longest, run)
        end = days[-1]
        if not daily[end]:
            end -= timedelta(days=1)
        current = 0
        while daily.get(end, 0):
            current += 1
            end -= timedelta(days=1)
        repos, page = [], 1
        while True:
            batch = request(f'https://api.github.com/users/{username}/repos?per_page=100&type=owner&page={page}')
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        totals = defaultdict(int)
        for repo in repos:
            if not repo['fork']:
                for name, size in request(repo['languages_url']).items():
                    totals[name] += size
        colors = ['#B7A9DE', '#78A6C2', '#8FBF9F', '#8B877E', '#B7A9DE', '#78A6C2']
        total_bytes = sum(totals.values()) or 1
        languages = [{'name': name, 'bytes': size, 'pct': round(size / total_bytes * 100, 2), 'color': colors[i]}
                     for i, (name, size) in enumerate(sorted(totals.items(), key=lambda pair: pair[1], reverse=True)[:6])]
        data = {'username': username, 'updated_at': datetime.now(timezone.utc).isoformat(),
                'total_contributions': sum(daily.values()), 'active_days': sum(n > 0 for n in daily.values()),
                'best_week': max(weekly.values()), 'current_streak': current, 'longest_streak': longest,
                'total_commits': None, 'total_prs': None, 'public_repos': len(repos),
                'weekly_contributions': list(weekly.values()), 'month_labels': labels, 'languages': languages,
                'daily_contributions': daily_contributions}
        if token:
            try:
                result = request('https://api.github.com/graphql', {
                    'query': 'query($login:String!){user(login:$login){contributionsCollection{totalCommitContributions totalPullRequestContributions}}}',
                    'variables': {'login': username}})
                counts = result['data']['user']['contributionsCollection']
                data['total_commits'] = counts['totalCommitContributions']
                data['total_prs'] = counts['totalPullRequestContributions']
            except (KeyError, TypeError, OSError):
                print('Annual commit/PR counts unavailable; displayed as a dash.')
        return data
    except (OSError, ValueError, KeyError) as error:
        print(f'Could not refresh profile data: {error}')
        return None
