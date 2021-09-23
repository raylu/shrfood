'use strict';

(async () => {
	const res = await fetch('food_tweets.json');
	const data = await res.json();

	const section = document.querySelector('section');
	for (const tweet of data) {
		const article = document.createElement('article');
		article.innerText = tweet.text;
		for (const media_id of tweet['images']) {
			const img = document.createElement('img');
			img.src = `img/${media_id}.webp`;
			img.loading = 'lazy';
			article.append(img);
		}
		section.append(article);
	}
})();
