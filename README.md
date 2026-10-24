# jmsb.info

The 1st Joint Multi-Functional Strike Battalion's public site. A plain
[Astro](https://astro.build) site: seven pages, no framework, no docs theme.

| Page | File | What |
|---|---|---|
| Home | `src/pages/index.astro` | one screen: the logo, the name, one line, Join and About, the next operation counting down, the three servers |
| Unit | `src/pages/unit.astro` | who we are, what we are, what we ask, how we run, ranks, the mods, questions |
| Roles | `src/pages/roles.astro` | the two halves of a player: roles (mission-based, from PAC's order of battle) and skills (what each qualification does), and the layered arsenal |
| Roster | `src/pages/roster.astro` | identification cards: the member's photo from PAC (or the patch), rank with insignia, pay grade, assignment, enlistment, qualifications in full; staff first, then everyone else, each by rank |
| SOP | `src/pages/sop.astro` | the standard operating procedures |
| Events | `src/pages/events.astro` | the calendar: next up, coming up, played |
| To be decided | `src/pages/tbd.astro` | the open questions - weapons, medical - with where we are and the choices |
| Wiki | - | a link to TAC//PAC's wiki |

## Where the words come from

- **TAC//PAC's public feed** (`https://pac.jmsb.info/?page=feed&what=...`) -
  the order of battle, the roster and the events are read in the visitor's
  browser (`src/scripts/pac.js`), so the site is always current. The SOP is not
  from PAC: its text is `src/data/sop.html` in this repository, edited here and
  dressed by `src/pages/sop.astro` at build time.
- **`src/data/site.json`** - the unit's name, tagline, the PAC address, the
  Discord invite, the Workshop link and the servers. Empty Discord or Workshop
  links are shown as placeholders.
- **The pages themselves** - the About text, the operation-night cards, the
  mods and the FAQ are written in `unit.astro`.

The home hero draws a contour map until a screenshot replaces it.

## Build and deploy

```
npm install
npm run dev        # http://localhost:4321
npm run build      # dist/
```

The site is static, served by nginx (`jmsb-info.conf`) on the Lightsail box
from a **git checkout** at `/var/www/jmsb.info`, built there - the way the
PAC sites are checkouts that pull (user, 2026-10-23: "fix that so it pulls
from git"). Astro 7 needs node 22, so the box has `nodejs22` beside its node 18.

Update, once `main` is pushed:

```
cd /var/www/jmsb.info && sudo ./scripts/update-server.sh
```

That pulls (`--ff-only`), runs `npm ci`, builds `dist/` and makes it readable;
nginx's root is `/var/www/jmsb.info/dist`. The one-time setup is in the
script's header. The old hand-copied root is kept as
`/var/www/jmsb.info.copied_20261023`.

## Server status

The home page shows each server live - online or not, players, the mission
and map - and opens a detail panel (state, version, locked, who is on and
for how long) when a server is clicked (user, 2026-10-23). A browser cannot
speak UDP, so the box does the asking: `scripts/arma-status.mjs` queries every
server in `site.json` over Steam's A2S protocol (query port = game port + 1)
and writes `/var/lib/jmsb-status/arma.json`, which nginx serves as
`/status/arma.json`; a systemd timer runs it every minute. One-time setup:
`cd /var/www/jmsb.info && sudo ./scripts/status-server-setup.sh`. Locally,
`node scripts/arma-status.mjs` prints the same JSON; the dev server has no
`/status/`, so the page shows "no status" there.

`public/steam/` holds the images in the mod's Steam Workshop description. Steam
draws them with `crossorigin="anonymous"`, so `jmsb-info.conf` has a
`location /steam/` block that sends `Access-Control-Allow-Origin: *` - without
it the images do not show on Steam (added 2026-10-17).
