'''
builtin pre_fetch event handler

apply host-specific or domain-specific defaults to:

 useragent
 proxy
 modifying url and headers['Host'] for mocking purposes
 cookie jar: defective, domain-specific, etc
 others: dns, ?

this code is currently fetcher:apply_url_policies()

Needs a more generic return value, some kid of "single url crawl" dict
'''
