#!/usr/bin/env python
#-*- coding:utf-8 -*-

import dns.resolver
import pytld

class PyDnsFeature(): 
    """
    dns feature
    """
    def __init__(self, dic): 
        pass

    def range(self):
        return 4

    def norm_dict(self): 
        d = {}
        d[0] = (0.0, 10.0)
        d[1] = (0.0, 10.0)
        d[2] = (0.0, 10.0)
        d[3] = (0.0, 1.0)
        return d

    def neednorm(self):
        """
        neednorm
        """
        return True

    def __dns_info(self, site): 
        chain_res = []
        ns_res = []
        try: 
            A = dns.resolver.query(site)
            chain_res = [[j.to_text() for j in i] for i in A.response.answer ]
        except Exception as e: 
            pass
        try: 
            ns = dns.resolver.query(pytld.get_tld(site),'NS') 
            ns_res = [[j.to_text() for j in i] for i in ns.response.answer ]
        except Exception as e: 
            pass
        return chain_res, ns_res, site
    
    def feature(self, site):
        info = self.__dns_info(site)
        chain_len = len(info[0])
        if chain_len != 0: 
            a_len = len(info[0][-1])
        else: 
            a_len = 0
        if len(info[1]) != 0: 
            ns_len = len(info[1][-1])
            ns_dm = set([pytld.get_tld(site) for site in info[1][-1]])
        else: 
            ns_len = 0
            ns_dm = set()
        same_ns = pytld.get_tld(info[2]) in ns_dm 
        return [(0, chain_len), (1, a_len), (2, ns_len), (3, 1 if same_ns else 0)]


if __name__ == '__main__':
    f = PyDnsFeature({})
    while True: 
        iput = raw_input()
        info = f.feature(iput)
        print info

