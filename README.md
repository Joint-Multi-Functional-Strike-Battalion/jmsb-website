# jmsb.info

The 1st Joint Multi-Functional Strike Battalion's public site. A plain
[Astro](https://astro.build) site: seven pages, no framework, no docs theme.

| Page | File | What |
|---|---|---|
| Home | `src/pages/index.astro` | one screen: the logo, the name, one line, Join and About, the next operation counting down, the three servers |
| Unit | `src/pages/unit.astro` | who we are, what we are, what we ask, how we run, ranks, the mods, questions |
| Roles | `src/pages/roles.astro` | the two halves of a player: roles (mission-based, from PAC's order of battle) and skills (what each qualification does), and the layered arsenal |
| Roster | `src/pages/roster.astro` | staff (the PAC admins) first, then everyone else: rank, qualifications, status, enlistment - written out, no abbreviations |
| SOP | `src/pages/sop.astro` | the standard operating procedures |
| Events | `src/pages/events.astro` | the calendar: next up, coming up, played |
| To be decided | `src/pages/tbd.astro` | the open questions - weapons, medical - with where we are and the choices |
| Wiki | - | a link to TAC//PAC's wiki |

## Where the words come from

- **TAC//PAC's public feed** (`https://pac.jmsb.info/?page=feed&what=...`) -
  the order of battle, the roster and the events are read in the visitor's
  browser (`src/scripts/pac.js`), so the site is always current. The SOP is a
  public page in PAC's wiki, read when the site is built; `src/data/sop-fallback.html`
  stands in when PAC cannot be reached at build time.
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

The site is static. Copy `dist/` to `/var/www/jmsb.info` on the Lightsail box
(nginx, `jmsb-info.conf`).
