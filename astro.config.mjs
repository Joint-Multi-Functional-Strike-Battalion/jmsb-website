// @ts-check
import { defineConfig } from 'astro/config';

// jmsb.info - the 1st Joint Multi-Functional Strike Battalion's public site.
// A plain Astro site: five pages, no framework, no docs theme. The wiki lives
// in TAC//PAC (pac.jmsb.info); this site reads PAC's public feed for the
// roster, the order of battle, the events and the SOP (src/scripts/pac.js).
export default defineConfig({
	site: 'https://jmsb.info',
	trailingSlash: 'ignore',
	build: { format: 'directory' },
});
