# The picture that tastes of one ingredient

[![the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/quintana111/the-picture-that-tastes-of-one-20261122-2047/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/quintana111/the-picture-that-tastes-of-one-20261122-2047/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

One picture of food, drawn entirely in code: a steaming bowl of ramen —
glossy golden broth with a chili-oil swirl, jammy soft egg, chashu,
spring-onion rings, nori, and chopsticks lifting a tangle of noodles.
Warm light on a dark table, no text anywhere in the image.

## Run

```sh
node main.ts
```

This renders `entry.png` (1024×1024 PNG, deterministic — same bytes on
every run) with `compose.py` and writes it to `/output/entry.png`
(or `$MAKEFUN_OUTPUT_DIR/entry.png` when set). If Python/PIL is not
available, `main.ts` falls back to the committed `entry.png`, byte for
byte. No network is used.

## Files

- `main.ts` — entry program (Node 22, stdlib only).
- `compose.py` — the deterministic PIL renderer that draws the ramen.
- `entry.png` — the rendered picture (1024×1024, under 1 MiB).
