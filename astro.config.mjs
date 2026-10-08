// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// jmsb.info - the 1st Joint Multi-Functional Strike Battalion's public site.
// Styled after the "Roles and Skills" briefing deck: Oswald headings, Public
// Sans text, slate ground, warm white ink, brass accent (src/styles/jmsb.css).
export default defineConfig({
	site: 'https://jmsb.info',
	integrations: [
		starlight({
			title: '1st JMSB',
			description: '1st Joint Multi-Functional Strike Battalion - an Arma 3 milsim unit.',
			logo: { src: './src/assets/jmsb-logo.png', alt: '1st JMSB crossed arrows' },
			favicon: '/favicon.png',
			customCss: ['./src/styles/jmsb.css'],
			head: [
				{ tag: 'link', attrs: { rel: 'preconnect', href: 'https://fonts.googleapis.com' } },
				{ tag: 'link', attrs: { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true } },
				{
					tag: 'link',
					attrs: {
						rel: 'stylesheet',
						href: 'https://fonts.googleapis.com/css2?family=Oswald:wght@400..700&family=Public+Sans:wght@400;600;700&display=swap',
					},
				},
			],
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/Joint-Multi-Functional-Strike-Battalion' },
			],
			sidebar: [
				{
					label: 'The unit',
					items: [
						{ label: 'About', slug: 'about' },
						{ label: 'Roles and skills', slug: 'roles' },
						{ label: 'Join', slug: 'join' },
					],
				},
				{
					label: 'Play',
					items: [
						{ label: 'Servers', slug: 'servers' },
						{ label: 'The mod', slug: 'mod' },
						{ label: 'TAC//PAC', link: 'https://pac.jmsb.info', attrs: { target: '_blank' } },
					],
				},
			],
		}),
	],
});
