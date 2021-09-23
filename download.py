#!/usr/bin/env python3

import json
import operator
import os
import subprocess

import httpx
import toml

def main():
	with open('config.toml', 'r', encoding='utf-8') as f:
		config = toml.load(f)['shrfood']

	try:
		os.mkdir('www/img')
	except FileExistsError:
		pass

	last_tweet_id = config.get('last_tweet_id')
	food_tweets, last_tweet_id = process_tweets(config['twitter_bearer_token'], last_tweet_id)

	try:
		with open('www/food_tweets.json', 'r', encoding='utf-8') as f:
			old_food_tweets = json.load(f)
			food_tweets.extend(old_food_tweets)
	except FileNotFoundError:
		pass
	food_tweets.sort(key=operator.itemgetter('id'), reverse=True)

	with open('www/food_tweets.json', 'w', encoding='utf-8') as f:
		json.dump(food_tweets, f, indent='\t')

	with open('config.toml', 'w', encoding='utf-8') as f:
		config['last_tweet_id'] = last_tweet_id
		toml.dump({'shrfood': config}, f)

def process_tweets(bearer_token, last_tweet_id):
	client = httpx.Client()
	food_tweets = []
	new_last_tweet_id = None
	for tweet in iter_tweets(client, bearer_token, last_tweet_id):
		if new_last_tweet_id is None:
			new_last_tweet_id = tweet['id_str']

		media = tweet['extended_entities'].get('media')
		if not media:
			continue

		discord_link = tweet['entities']['urls'][0]
		text = tweet['text']
		text = text[:discord_link['indices'][0] - 1]
		images = []
		for m in media:
			if m['type'] == 'photo':
				images.append(download_image(client, m))
			else:
				print(tweet['id_str'])
				print(m)

		food_tweets.append({
			'id': tweet['id_str'],
			'text': text,
			'discord_link': discord_link['expanded_url'],
			'images': images,
		})

	if new_last_tweet_id is None:
		new_last_tweet_id = last_tweet_id
	return food_tweets, new_last_tweet_id

def iter_tweets(client, bearer_token, last_tweet_id):
	if last_tweet_id is None:
		# first run; iterate backwards through tweets
		max_id = None
	else:
		# iterate forwards since last_tweet_id
		since_id = last_tweet_id

	while True:
		params = {
			'screen_name': 'shrfood',
			'count': 200,
			'trim_user': True,
			'exclude_replies': True,
		}
		if last_tweet_id is None:
			if max_id is not None:
				params['max_id'] = max_id
		else:
			params['since_id'] = since_id
		r = client.get('https://api.twitter.com/1.1/statuses/user_timeline.json', params=params,
			headers={'Authorization': 'Bearer ' + bearer_token})
		r.raise_for_status()
		tweets = r.json()
		if not tweets:
			break
		if last_tweet_id is None:
			max_id = tweets[-1]['id'] - 1
		else:
			since_id = tweets[0]['id_str']

		for tweet in tweets:
			yield tweet

def tweet_id_to_ts(tweet_id):
	# https://github.com/client9/snowflake2time#snowflake-layout
	return (tweet_id & 0x7fffffffffffffff) >> 22

def download_image(client, m):
	for retry in range(3):
		r = client.get(m['media_url_https'] + ':medium')
		if r.status_code == 200:
			filepath = 'www/img/' + m['id_str']
			with open(filepath, 'wb') as f:
				f.write(r.content)
			break
		else:
			print('retry', retry, r)
	else:
		r.raise_for_status()

	subprocess.run(['cwebp', '-preset', 'photo', '-mt', '-quiet',
		filepath, '-o', filepath + '.webp'], check=True)

	os.remove(filepath)
	return m['id_str']

if __name__ == '__main__':
	main()
