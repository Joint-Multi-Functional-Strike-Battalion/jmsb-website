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

/* PAC's names are short and upper case - "TEAM 2 MECH", "SPT TEAM AVN DET",
 * a role called "JFO / Strike". The site writes them out. */
const WORDS = {
	HHC: 'Headquarters', HHD: 'Headquarters', C2: 'Command', TEAM: 'Team', COY: 'Company',
	INF: 'Infantry', MECH: 'Mechanised', SPT: 'Support', AVN: 'Aviation', DET: 'Detachment',
	DRONES: 'Drones', FIRES: 'Fires', PLT: 'Platoon', SQD: 'Squad', VEC: 'Vehicle',
};
const TERMS = {
	JFO: 'Joint Fires Observer', ISR: 'Intelligence, Surveillance and Reconnaissance',
	UAV: 'Drone Operator', EOD: 'Explosive Ordnance Disposal', CLS: 'Combat Lifesaver',
	MED: 'Medic', ENG: 'Engineer', ATL: 'Assistant Team Lead', TL: 'Team Lead',
	CAS: 'Close Air Support', MKS: 'Marksman', SNP: 'Sniper', BRC: 'Breacher',
};

/** "SPT TEAM AVN DET" -> "Support Team Aviation Detachment"; "GHOST 1-1" -> "Ghost 1-1". */
export function expand(s) {
	return String(s ?? '').trim().split(/\s+/).filter(Boolean).map((w) => {
		const u = w.toUpperCase();
		if (WORDS[u]) return WORDS[u];
		if (/^\d/.test(w)) return w;
		return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
	}).join(' ');
}

/** Spell out the terms a role or skill name abbreviates: "JFO / Strike" -> "Joint Fires Observer / Strike". */
export function words(s) {
	return String(s ?? '').replace(/\b[A-Z]{2,4}\b/g, (w) => TERMS[w] || w);
}

/** A skill's full name from the feed, written out. */
export function skillName(skill, id) {
	const n = skill && skill.name ? skill.name : String(id ?? '');
	return TERMS[n.toUpperCase()] || words(n);
}

/* A contour map, drawn rather than photographed: a value-noise field cut into
 * contour lines in the brass, with a faint grid, on the slate ground. Behind
 * the home hero and the next-operation poster. */
export function contours(canvas, host, seed = 0) {
	const hash = (x, y) => { const h = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return h - Math.floor(h); };
	const smooth = (t) => t * t * (3 - 2 * t);
	const noise = (x, y) => {
		const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
		const a = hash(xi, yi), b = hash(xi + 1, yi), c = hash(xi, yi + 1), d = hash(xi + 1, yi + 1);
		const u = smooth(xf), v = smooth(yf);
		return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
	};
	const field = (x, y) => noise(x, y) * 0.6 + noise(x * 2.1 + 5, y * 2.1 + 9) * 0.28 + noise(x * 4.3 + 1, y * 4.3 + 3) * 0.12;
	const draw = () => {
		const w = host.clientWidth, h = host.clientHeight, dpr = Math.min(window.devicePixelRatio || 1, 2);
		if (!w || !h) return;
		canvas.width = w * dpr; canvas.height = h * dpr;
		const ctx = canvas.getContext('2d');
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
		ctx.fillStyle = '#20261c'; ctx.fillRect(0, 0, w, h);
		const cell = 8, cols = Math.ceil(w / cell) + 1, rows = Math.ceil(h / cell) + 1, s = 1 / 170, vals = [];
		for (let j = 0; j < rows; j++) { vals[j] = []; for (let i = 0; i < cols; i++) vals[j][i] = field(i * cell * s + 11 + seed, j * cell * s + 7 + seed * 0.7); }
		for (let L = 0; L < 14; L++) {
			const lvl = 0.22 + L * 0.04;
			ctx.strokeStyle = L % 5 === 0 ? 'rgba(194,168,120,0.42)' : 'rgba(194,168,120,0.16)';
			ctx.lineWidth = L % 5 === 0 ? 1.4 : 1;
			ctx.beginPath();
			for (let j = 0; j < rows - 1; j++) for (let i = 0; i < cols - 1; i++) {
				const a = vals[j][i], b = vals[j][i + 1], c = vals[j + 1][i + 1], d = vals[j + 1][i];
				const x = i * cell, y = j * cell, p = [];
				if ((a < lvl) !== (b < lvl)) p.push([x + cell * (lvl - a) / (b - a), y]);
				if ((b < lvl) !== (c < lvl)) p.push([x + cell, y + cell * (lvl - b) / (c - b)]);
				if ((d < lvl) !== (c < lvl)) p.push([x + cell * (lvl - d) / (c - d), y + cell]);
				if ((a < lvl) !== (d < lvl)) p.push([x, y + cell * (lvl - a) / (d - a)]);
				if (p.length >= 2) { ctx.moveTo(p[0][0], p[0][1]); ctx.lineTo(p[1][0], p[1][1]); }
				if (p.length === 4) { ctx.moveTo(p[2][0], p[2][1]); ctx.lineTo(p[3][0], p[3][1]); }
			}
			ctx.stroke();
		}
		ctx.strokeStyle = 'rgba(233,228,211,0.06)'; ctx.lineWidth = 1; ctx.beginPath();
		for (let gx = 0; gx < w; gx += 96) { ctx.moveTo(gx + .5, 0); ctx.lineTo(gx + .5, h); }
		for (let gy = 0; gy < h; gy += 96) { ctx.moveTo(0, gy + .5); ctx.lineTo(w, gy + .5); }
		ctx.stroke();
	};
	draw();
	let rt;
	window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(draw, 120); });
}

/** Escape for the one place markup is built from data. */
export function esc(s) {
	return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
