#!/usr/bin/env node
/* Server status for the home page (user, 2026-10-23: "add a server status ...
 * monitor our arma server 172.93.101.237:2302 ... on front page a status and if
 * you click on a server more details").
 *
 * A browser cannot speak UDP, so this runs on the box: it asks every server in
 * src/data/site.json over Steam's A2S protocol (the query port is the game
 * port + 1) - A2S_INFO for the name, map, mission, player count, state and
 * version, A2S_PLAYER for who is on and for how long - and writes one JSON
 * file that nginx serves as /status/arma.json. The home page reads that file.
 * No dependencies: node's dgram only.
 *
 *   node scripts/arma-status.mjs                prints the JSON
 *   node scripts/arma-status.mjs /path/out.json writes it (the systemd timer)
 *
 * On the box: scripts/status-server-setup.sh installs the timer and the
 * nginx location.
 */
import dgram from 'node:dgram';
import { readFileSync, writeFileSync, mkdirSync, renameSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SITE = JSON.parse(readFileSync(join(HERE, '..', 'src', 'data', 'site.json'), 'utf8'));
const TIMEOUT_MS = 2500;
const QUERY_PORT_OFFSET = 1;
const HEADER = Buffer.from([0xff, 0xff, 0xff, 0xff]);
const A2S_INFO = Buffer.concat([HEADER, Buffer.from('TSource Engine Query\0', 'latin1')]);
const A2S_PLAYER = Buffer.concat([HEADER, Buffer.from('U'), Buffer.from([0xff, 0xff, 0xff, 0xff])]);
// Arma 3's "s" keyword: what the server is doing.
const STATES = {
	0: 'no mission', 1: 'selecting a mission', 2: 'editing a mission', 3: 'assigning roles', 4: 'sending the mission',
	5: 'loading', 6: 'briefing', 7: 'playing', 8: 'debriefing', 9: 'mission aborted',
};

/** One UDP exchange: send, wait for one reply, answer a challenge (0x41) once. */
function ask(host, port, request, rebuild) {
	return new Promise((resolve, reject) => {
		const sock = dgram.createSocket('udp4');
		let challenged = false;
		const timer = setTimeout(() => { sock.close(); reject(new Error('timeout')); }, TIMEOUT_MS);
		sock.on('error', (e) => { clearTimeout(timer); sock.close(); reject(e); });
		sock.on('message', (msg) => {
			if (msg.length >= 9 && msg[4] === 0x41 && !challenged) {
				challenged = true;
				sock.send(rebuild(msg.subarray(5, 9)), port, host);
				return;
			}
			clearTimeout(timer);
			sock.close();
			resolve(msg);
		});
		sock.send(request, port, host);
	});
}

class Reader {
	constructor(buf, at) { this.b = buf; this.i = at; }
	u8() { return this.b[this.i++]; }
	u16() { const v = this.b.readUInt16LE(this.i); this.i += 2; return v; }
	i32() { const v = this.b.readInt32LE(this.i); this.i += 4; return v; }
	f32() { const v = this.b.readFloatLE(this.i); this.i += 4; return v; }
	u64() { this.i += 8; }
	str() { const end = this.b.indexOf(0, this.i); const s = this.b.toString('utf8', this.i, end < 0 ? this.b.length : end); this.i = end < 0 ? this.b.length : end + 1; return s; }
}

function parseInfo(msg) {
	const r = new Reader(msg, 5);
	const info = {};
	r.u8(); // protocol
	info.serverName = r.str();
	info.map = r.str();
	r.str(); // folder
	info.mission = r.str();
	r.u16(); // app id
	info.players = r.u8();
	info.max = r.u8();
	r.u8(); // bots
	r.u8(); r.u8(); // type, environment
	info.password = r.u8() === 1;
	r.u8(); // vac
	info.version = r.str();
	const edf = r.i < msg.length ? r.u8() : 0;
	if (edf & 0x80) r.u16();
	if (edf & 0x10) r.u64();
	if (edf & 0x40) { r.u16(); r.str(); }
	if (edf & 0x20) {
		info.keywords = r.str();
		const kv = {};
		for (const k of info.keywords.split(',')) if (k) kv[k[0]] = k.slice(1);
		if (kv.s !== undefined) info.state = STATES[Number(kv.s)] || `state ${kv.s}`;
		info.battleye = kv.b === 't';
		info.locked = kv.l === 't'; // the admin's #lock, apart from a password
	}
	return info;
}

function parsePlayers(msg) {
	const r = new Reader(msg, 5);
	const n = r.u8();
	const out = [];
	for (let i = 0; i < n && r.i < msg.length; i++) {
		r.u8(); // index
		const name = r.str();
		const score = r.i32();
		const seconds = r.f32();
		if (name) out.push({ name, score, seconds: Math.round(seconds) });
	}
	out.sort((a, b) => b.seconds - a.seconds);
	return out;
}

async function query(server) {
	const port = server.port + QUERY_PORT_OFFSET;
	const t0 = Date.now();
	const row = { name: server.name, host: server.host, port: server.port, online: false };
	try {
		const info = await ask(server.host, port, A2S_INFO, (ch) => Buffer.concat([A2S_INFO, ch]));
		if (info[4] !== 0x49) throw new Error(`unexpected reply 0x${info[4].toString(16)}`);
		Object.assign(row, parseInfo(info), { online: true, ping: Date.now() - t0 });
		try {
			const players = await ask(server.host, port, A2S_PLAYER, (ch) => Buffer.concat([HEADER, Buffer.from('U'), ch]));
			if (players[4] === 0x44) row.playerList = parsePlayers(players);
		} catch (e) {
			row.playerList = null; // the count above still stands
		}
	} catch (e) {
		row.error = String(e.message || e);
	}
	return row;
}

const servers = await Promise.all(SITE.servers.map(query));
const out = { generated: new Date().toISOString(), servers };
const text = JSON.stringify(out, null, 1);
const target = process.argv[2];
if (target) {
	mkdirSync(dirname(target), { recursive: true });
	// Written beside and renamed, so nginx never serves a half-written file.
	writeFileSync(target + '.tmp', text);
	renameSync(target + '.tmp', target);
} else {
	console.log(text);
}
