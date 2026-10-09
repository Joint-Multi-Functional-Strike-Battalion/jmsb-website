// Pull the SmartCards decks from the mod repo. The JSON is the master and
// lives in jmsb-custom-mod (docs/acm-smart-cards.json and its images); this
// site keeps a copy under src/content/smartcards/<deck>.json and the images
// the deck names under public/smartcards/<deck>/. Run: npm run cards:pull
import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const site = resolve(here, '..');
const mod = process.env.JMSB_MOD || resolve(site, '..', 'jmsb-custom-mod');

// deck slug -> the deck's JSON in the mod repo
const DECKS = { acm: 'docs/acm-smart-cards.json' };

for (const [deck, rel] of Object.entries(DECKS)) {
	const src = join(mod, rel);
	const dst = join(site, 'src', 'content', 'smartcards', `${deck}.json`);
	copyFileSync(src, dst);
	const data = JSON.parse(readFileSync(src, 'utf8'));
	const out = join(site, 'public', 'smartcards', deck);
	mkdirSync(out, { recursive: true });
	for (const [key, path] of Object.entries(data.assets || {})) {
		if (key === 'logo') continue; // the site has its own logo
		const ext = path.slice(path.lastIndexOf('.'));
		copyFileSync(join(mod, path), join(out, `${key}${ext}`));
		console.log(`${deck}: ${key}${ext}`);
	}
	console.log(`${deck}: ${data.cards.length} cards, version ${data.version}`);
}
