'''
Code related to data storage for domains and hosts.

Should be part of the datalayer... XXX
'''

# host
#  histogram of 200s first_byte_t
#  politeness level
#  towww tohttps etc
#  hyperloglog count of unique 200s
#  hyperloglog of path elemnts
#  hyperloglog of host-level cgi arg names
#  something with frags -- url level? 2-level of urls and frags
#  per-host crawl queue divided by priority levels
#  per-host seen

# domain
#  list of hosts - could be 10s of thousands if the public suffix private list fails on us, so keep them all
# 
