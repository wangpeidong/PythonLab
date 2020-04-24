from multiprocessing import Pool
import bs4 as bs
import random
import requests
import string

def random_starting_url():
	starting = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(3))
	url = ''.join(['http://', starting, '.com'])
	return url

def handle_local_links(url, link):
	if link.startswith('/'):
		return ''.join([url, link])
	elif link.startswith('http'):
		return link

def get_links(url):
	try:
		print(f'crawling {url}')		
		resp = requests.get(url)
		soup = bs.BeautifulSoup(resp.text, 'lxml')
		body = soup.body
		links = [link.get('href') for link in body.find_all('a')]
		links = [handle_local_links(url, link) for link in links]
		links = [link for link in links if link is not None]
		#links = [str(link.encode("ascii")) for link in links]
		return links        
	except TypeError as e:
		print(f'Exception: Got a TypeError, probably got a None that we tried to iterate over {e}')
		return []
	except IndexError as e:
		print(f'Exception: We probably did not find any useful links, returning empty list {e}')
		return []
	except AttributeError as e:
		print(f'Exception: Likely got None for links, so we are throwing this {e}')
		return []
	except KeyboardInterrupt as e:
		raise e
	except Exception as e:
		print(f'Exception: {str(e)}')
		# log this error 
		return []

def crawl():
	how_many = 50
	p = Pool(processes = how_many)
	parse_us = [random_starting_url() for _ in range(how_many)]

	data = p.map(get_links, [link for link in parse_us])
	data = [url for url_list in data for url in url_list]
	p.close()

	with open('urls.txt', 'w') as f:
		f.write(str(data))

if __name__ == '__main__':
	crawl()		
