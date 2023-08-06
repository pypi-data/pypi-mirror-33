#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 13:28:57 2018

@author: jeroen

source for van der Corput and Halton sampling code
https://laszukdawid.com/2017/02/04/halton-sequence-in-python/

def halton_sequence(size, dim):
    seq = []
    primeGen = next_prime()
    next(primeGen)
    for d in range(dim):
        base = next(primeGen)
        seq.append([vdc(i, base) for i in range(size)])
    return np.array(seq).T
"""

import numpy as np

def vdc(n, base=2):
    vdc, denom = 0,1
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc

def next_prime():
    def is_prime(num):
        "Checks if num is a prime value"
        for i in range(2,int(num**0.5)+1):
            if(num % i)==0: return False
        return True
 
    prime = 3
    while(1):
        if is_prime(prime):
            yield prime
        prime += 2

class HaltonSampler():
    def __init__(self, dim):
        self.dim = dim
        
        # setup primes for every dimension
        prime_factory = next_prime()
        self.primes = []
        for i in range(dim):
            self.primes.append(next(prime_factory))
        
        # init counter for van der Corput sampling
        self.cnt = 1
    
    def get_samples(self, n):
        seq = []
        for d in range(self.dim):
            base = self.primes[d]
            seq.append([vdc(i, base) for i in range(self.cnt, self.cnt+n)])
        self.cnt += n
        return np.array(seq).T