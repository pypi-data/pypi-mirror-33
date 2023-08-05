from entry.api.exceptions import RateLimitReached

class RateLimit:
    rate_limit = (100, 1, 'minute')

    def limit(self):
        cache = self.container.make('Cache')
        if not cache.is_valid('Entry/rate_limit/IP/' + self.request.environ['REMOTE_ADDR']):
            # create a new cache
            cache.store_for(
                'Entry/rate_limit/IP/' +
                self.request.environ['REMOTE_ADDR'], '1',
                self.rate_limit[1], self.rate_limit[2]
            )
            self.request.header('X-RateLimit-Limit', str(self.rate_limit[0]), http_prefix = None)
            self.request.header('X-RateLimit-Remaining', str(int(self.rate_limit[0]) - 1), http_prefix = None)
            return
        else:
            rate_limit = int(cache.get(
                'Entry/rate_limit/IP/' + self.request.environ['REMOTE_ADDR']
            )) + 1

            if rate_limit > self.rate_limit[0]:
                raise RateLimitReached

            cache.update(
                'Entry/rate_limit/IP/' + self.request.environ['REMOTE_ADDR'],
                rate_limit
            )
            # Set Headers
            self.request.header('X-RateLimit-Limit', str(self.rate_limit[0]), http_prefix = None)
            self.request.header('X-RateLimit-Remaining', str(int(self.rate_limit[0]) - rate_limit), http_prefix = None)
            return
        

