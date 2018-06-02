from requests import Session
from .objects import RateLimit, NationAPI, RegionAPI, WorldAPI, WorldAssemblyAPI
from .exceptions import RateLimitReached

class Api:
    def __init__(self, user_agent, version="9",
        ratelimit_sleep=False,
        ratelimit_max=48,
        ratelimit_within=30):
        self.user_agent = user_agent
        self.version = version
        self.session = Session()
        self.ratelimitsleep = ratelimit_sleep
        self.ratelimit_max = ratelimit_max
        self.ratelimit_within = ratelimit_within
        self.xrls = 0
        self.rlobj = RateLimit()

    def rate_limit(self, new_xrls=1):
        # Raises an exception if RateLimit is either banned 
        self.xrls = int(new_xrls)
        self.rlobj.add_timestamp()

    def check_ratelimit(self):
        rlflag = self.rlobj.ratelimitcheck(xrls=self.xrls,
                amount_allow=self.ratelimit_max,
                within_time=self.ratelimit_within)
        if not rlflag:
        	raise RateLimitReached("The Rate Limit was too close the API limit to safely handle this request")

    def Nation(self, name):
        return NationAPI(name, self)

    def PrivateNation(self, name, password=None, autologin=None):
        return PrivateNationAPI(name, self, password=password, autologin=autologin)

    def Region(self, name):
        return RegionAPI(name, self)

    def World(self):
        return WorldAPI(self)

    def WorldAssembly(self, chamber):
    	return WorldAssemblyAPI(chamber, self)
    	