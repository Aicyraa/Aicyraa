# Profile graphics

The README contains a transparent SVG panel with a dark blue border with a terminal profile on the left and live contribution analytics on the right. GitHub strips CSS flexbox from README markup, so both columns are composed into one SVG for a stable side-by-side layout. Orange accents highlight the terminal commands and best-week statistic.

A matching transparent terminal About panel follows it, introducing the profile as “A builder” with details about projects, languages, and current interests. The standalone name header, contact icons, and projects section have been removed from the README. Streak values and labels are centered within two equal columns without an underline. The centered toolkit contains 20 monochrome logos, including Prisma, Neon, Supabase, Vercel, Vitest, Jest, Bruno, and Postman.

## Editing

- `README.md`: visible sections, sizing, and alternative text.
- `scripts/profile_design.py`: terminal contents and current focus, container layout, palette, section headings, and tool grid.
- `assets/icons/`: added SVG logos from [Simple Icons](https://github.com/simple-icons/simple-icons).
- `assets/stack-reference.svg`: original technology marks, retained from the initial [reference profile](https://github.com/Himanshu-MlSHRA/Himanshu-MlSHRA).
- `scripts/generate_stats.py`, `generate_streak.py`, `generate_langs.py`: contribution and language chart renderers. Their original palette is mapped to the current blue and orange colors during rendering.

Embedded JetBrains Mono fonts are retained from the initial adaptation. All SVGs render immediately without animation or external image services.

## Refresh

```sh
python scripts/generate.py Aicyraa
```

Python 3.12 is used in Actions. No third-party Python dependencies are required. After these files are pushed to `main`, the workflow refreshes the profile panel and analytics daily. It can also be started from **Actions → Refresh profile stats → Run workflow**.

To regenerate all artwork from the saved snapshot without network access:

```sh
python scripts/profile_design.py
```

## Data

The public GitHub contribution calendar supplies annual contributions, active days, weekly totals, and streaks, including partial weeks at either end. Longest streak refers to the calendar window. The current streak allows today to be unfinished.

Language percentages use bytes across public, non-fork repositories and describe repository contents, not proficiency. The public repository counter includes forks. Failed fetches preserve the last successful snapshot.

The workflow uses the automatic `GITHUB_TOKEN`. An optional `GH_PAT` secret can provide annual commit and pull request counts in the saved data, but those fields are not displayed. Recent events are never substituted for annual contribution totals.
