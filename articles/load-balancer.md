---
title: "Building an HTTP load balancer in Python"
date: "2026-08-20"
tags: [python, networking, projects]
---

# Building an HTTP load balancer

I built a HTTP proxy & load balancer with aiohttp. Here's what it supports:

## Features

- **Weighted round-robin** — distribute requests based on backend capacity
- **Sticky sessions** — route same client to same backend
- **Circuit breaker** — stop sending requests to failing backends
- **Backpressure** — slow down when backends are overwhelmed
- **Connection pooling** — reuse connections to reduce latency

## Why

To understand how production load balancers work under the hood.

## Code

Check it out on [GitHub](https://github.com/n0rdii/load-balancer).

```python
# Simplified round-robin
class RoundRobin:
    def __init__(self, backends):
        self.backends = backends
        self.idx = 0

    def next(self):
        backend = self.backends[self.idx]
        self.idx = (self.idx + 1) % len(self.backends)
        return backend
```
