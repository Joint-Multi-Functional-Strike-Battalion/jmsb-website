# jmsb.info

The public site of the 1st Joint Multi-Functional Strike Battalion, built with
[Astro](https://astro.build) and [Starlight](https://starlight.astro.build).
Styled after the battalion's "Roles and Skills" briefing deck: Oswald headings,
Public Sans text, slate ground and brass accent (`src/styles/jmsb.css`).

## Pages

Markdown/MDX in `src/content/docs/` - one file per page:

| File | Page |
|---|---|
| `index.mdx` | Home (splash) |
| `about.mdx` | About the battalion |
| `roles.mdx` | Roles and skills |
| `join.mdx` | Join |
| `servers.mdx` | Servers |
| `mod.mdx` | The mod |

The sidebar is set in `astro.config.mjs`. Text in [square brackets] is a
placeholder still to be written.

## Build

Needs Node 22 or newer.

```sh
npm install
npm run dev      # local preview at http://localhost:4321
npm run build    # static site in dist/
```

## Deploy

The site is static. It is served by nginx on the battalion's Lightsail server
from `/var/www/jmsb.info` (config `/etc/nginx/conf.d/jmsb-info.conf`). To
publish, build, then copy `dist/` there:

```sh
npm run build
tar czf jmsb-dist.tgz -C dist .
scp -i <key> jmsb-dist.tgz ec2-user@35.93.34.227:/tmp/
ssh -i <key> ec2-user@35.93.34.227 \
  'sudo rm -rf /var/www/jmsb.info/* && sudo tar xzf /tmp/jmsb-dist.tgz -C /var/www/jmsb.info && sudo chmod -R a+rX /var/www/jmsb.info'
```

The TAC//PAC manager at https://pac.jmsb.info is a separate site (DIVINER_Web).
