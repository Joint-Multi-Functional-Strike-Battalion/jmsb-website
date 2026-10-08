/* What the site reads from TAC//PAC's public feed, and the two things every
 * page does with it: show a time in the visitor's own zone, and count down.
 *
 * The feed is JSON at <pac>/?page=feed&what=... - see the DIVINER_Web README.
 * Nothing here needs a login, and nothing is written. If the feed is off or
 * down, every caller falls back to what the page already shows.
 */
import site from '../data/site.json';

export const PAC = site.pac;

export async function feed(what, extra = {}) {
	const u = new URL(`${PAC}/`);
	u.searchParams.set('page', 'feed');
	u.searchParams.set('what', what);
	for (const [k, v] of Object.entries(extra)) u.searchParams.set(k, v);
	const r = await fetch(u, { cache: 'no-cache' });
	if (!r.ok) throw new Error(`feed ${what}: ${r.status}`);
	return r.json();
}

/** "Sat 11 Oct, 19:00" in the visitor's zone; `long` adds the year and zone name. */
export function when(iso, long = false) {
	const d = new Date(iso);
	if (Number.isNaN(d.getTime())) return '';
	const o = long
		? { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' }
		: { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
	return new Intl.DateTimeFormat(undefined, o).format(d);
}

/** The visitor's zone, for the "times are yours" note. */
export function zone() {
	try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch { return ''; }
}

/**
 * Fill four counters - [data-d], [data-h], [data-m], [data-s] inside `root` -
 * every second until the instant passes, then call `done`.
 */
export function countdown(root, iso, done) {
	const t = new Date(iso).getTime();
	if (Number.isNaN(t)) return;
	const cell = (k) => root.querySelector(`[data-${k}]`);
	const two = (n) => (n < 10 ? '0' : '') + n;
	let timer = 0;
	const tick = () => {
		const left = Math.floor((t - Date.now()) / 1000);
		if (left <= 0) { clearTimeout(timer); done && done(); return; }
		const d = Math.floor(left / 86400), h = Math.floor(left % 86400 / 3600), m = Math.floor(left % 3600 / 60), s = left % 60;
		cell('d').textContent = String(d);
		cell('h').textContent = two(h);
		cell('m').textContent = two(m);
		cell('s').textContent = two(s);
		timer = setTimeout(tick, 1000 - (Date.now() % 1000));
	};
	tick();
}

/** Escape for the one place markup is built from data. */
export function esc(s) {
	return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
