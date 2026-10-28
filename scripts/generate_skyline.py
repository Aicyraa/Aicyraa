"""Animated contribution skyline: one oblique box per day, no JavaScript."""
from datetime import date, timedelta
from math import sqrt
from html import escape
from profile_design import frame, text, BLUE, ORANGE, MUTED, INK


def shade(color, factor):
    return '#' + ''.join(f'{min(255, round(int(color[i:i+2],16)*factor)):02x}' for i in (1,3,5))


def generate_skyline_svg(data):
    days = sorted(data.get('daily_contributions', []), key=lambda day: day['date'])
    body = '<title>Animated skyline of daily GitHub contributions</title>'
    body += '<rect x=".5" y=".5" width="959" height="415" rx="12" fill="none" stroke="#2a3b51"/>'
    body += text(24, 29, 'contribution skyline', 11, BLUE)
    if not days:
        body += text(480, 215, 'Daily contributions will appear after the next successful refresh.', 12, MUTED, 'text-anchor="middle"')
        return frame(416, body, 960)
    start = date.fromisoformat(days[0]['date'])
    first_sunday = start - timedelta(days=(start.weekday()+1)%7)
    last = date.fromisoformat(days[-1]['date'])
    weeks = ((last-first_sunday).days//7)+1
    step = min(15, 820/max(1, weeks-1))
    peak = max(days, key=lambda day: day['count'])
    peak_count = peak['count']
    body += text(935, 29, f"{start:%d %b %Y} — {last:%d %b %Y}", 9, MUTED, 'text-anchor="end"')
    body += text(24, 71, f"{sum(day['count'] for day in days):,}", 26, INK)
    body += text(25, 92, 'contributions / last year', 10, MUTED)
    css = '''.city{animation:city-cycle 16s linear infinite}
@keyframes city-cycle{0%,88%{opacity:1}96%,100%{opacity:0}}
.peak-note{animation:peak-note 16s linear infinite}
@keyframes peak-note{0%,48%{opacity:0}54%,88%{opacity:1}96%,100%{opacity:0}}
'''
    for week in range(weeks):
        begin = week/max(1,weeks-1)*6/16*100
        end = (week/max(1,weeks-1)*6+.8)/16*100
        css += f'.week-{week}{{animation:rise-{week} 16s cubic-bezier(.22,.61,.36,1) infinite;transform-origin:0 0}}\n'
        css += f'@keyframes rise-{week}{{0%,{begin:.4f}%{{transform:scaleY(0)}}{end:.4f}%,99.99%{{transform:scaleY(1)}}100%{{transform:scaleY(0)}}}}\n'
    css += '@media(prefers-reduced-motion:reduce){.building,.city,.peak-note{animation:none!important;transform:none!important;opacity:1!important}}'
    body += f'<style>{css}</style>'
    body += '<path d="M43 333H852L894 291H85Z" fill="#172333" fill-opacity=".3"/>'
    buildings = []
    peak_point = None
    for day in days:
        actual = date.fromisoformat(day['date'])
        week = (actual-first_sunday).days//7
        row = (actual.weekday()+1)%7
        x, y = 48+week*step+(6-row)*6, 330-(6-row)*6
        count = day['count']
        height = 2+sqrt(count/max(1,peak_count))*170 if count else 1
        color = ['#243247','#415a73','#597996','#7597b6','#91adc9'][max(0,min(4,day['level']))]
        is_peak = day is peak and count>0
        if is_peak:
            color = ORANGE
            peak_point = (x+6, y-height-4)
        w,d=11.5,5
        faces = f'<path d="M0 {-height:.2f}H{w}V0H0Z" fill="{color}"/>'
        faces += f'<path d="M{w} 0L{w+d} -4V{-height-4:.2f}L{w} {-height:.2f}Z" fill="{shade(color,.70)}"/>'
        faces += f'<path d="M0 {-height:.2f}L{d} {-height-4:.2f}H{w+d}L{w} {-height:.2f}Z" fill="{shade(color,1.17)}"/>'
        title = escape(f"{actual:%d %b %Y}: {count} contributions")
        building = f'<g transform="translate({x:.2f} {y:.2f})"><title>{title}</title><g class="building week-{week}" data-date="{actual}" data-count="{count}">{faces}</g></g>'
        buildings.append((row, week, building))
    body += '<g class="city">'+''.join(item[2] for item in sorted(buildings))+'</g>'
    if peak_point:
        px,py=peak_point
        label_x=max(300,min(710,px+13))
        body += '<g class="peak-note">'
        body += f'<path d="M{px:.2f} {py:.2f}V107H{label_x}" stroke="{ORANGE}" stroke-opacity=".7" fill="none"/>'
        body += f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2.5" fill="{ORANGE}"/>'
        body += text(label_x, 76, f'{peak_count} contributions', 18, ORANGE)
        body += text(label_x, 95, f"{date.fromisoformat(peak['date']):%d %b %Y} / best day", 9, MUTED)
        body += '</g>'
    last_label = -100
    for week in range(weeks):
        day = first_sunday+timedelta(weeks=week)
        if week==0 or day.day<=7:
            x=48+week*step
            if x-last_label>=35:
                body += text(round(x,2), 359, day.strftime('%b'), 9, MUTED)
                last_label=x
    body += text(24, 391, 'one building / one day', 9, MUTED)
    body += text(935, 391, 'height = √contributions', 9, MUTED, 'text-anchor="end"')
    return frame(416, body, 960)
