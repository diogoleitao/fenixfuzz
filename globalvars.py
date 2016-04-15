from collections import deque

links_queue = deque([])
parsed_links_queue = deque([])
cookies = {}
base_url = "http://localhost:8080"
n_threads_crawler = 1
n_threads_requests = 1
