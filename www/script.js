'use strict';

(async () => {
	const res = await fetch('food_tweets.json');
	const data = await res.json();

	const main = document.querySelector('main');
	for (const tweet of data) {
		const article = document.createElement('article');

		const link = document.createElement('a');
		link.innerText = tweet['text'];
		link.href = tweet['discord_link'];
		article.append(link);

		const div = document.createElement('div');
		if (tweet['images'].length > 1)
			div.classList.add('multi');
		for (const media_id of tweet['images']) {
			const img = document.createElement('img');
			img.src = `img/${media_id}.webp`;
			img.loading = 'lazy';
			div.append(img);
		}
		article.append(div);

		main.append(article);
	}

	const modal = document.querySelector('div#modal');
	modal.addEventListener('click', (evt) => {
		modal.style.display = 'none';
		modal.innerHTML = '';
	});
	main.addEventListener('click', (evt) => {
		if (evt.target.loading !== 'lazy')
			return;
		const img = document.createElement('img');
		img.src = evt.target.src;
		modal.append(img);
		modal.style.display = 'flex';
	});
})();
