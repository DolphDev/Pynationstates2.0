from requests import Session
from time import sleep
from .objects import RateLimit, NationAPI, RegionAPI, WorldAPI, WorldAssemblyAPI, TelegramAPI
from .exceptions import RateLimitReached

class Api:
    def __init__(self, user_agent, version="9",
        ratelimit_sleep=False,
        ratelimit_sleep_time=4,
        ratelimit_max=48,
        ratelimit_within=30,
        ratelimit_maxsleeps=10,
        ratelimit_enabled=True):
        self.user_agent = user_agent
        self.version = version
        self.session = Session()
        self.ratelimitsleep = ratelimit_sleep
        self.ratelimitsleep_time = ratelimit_sleep_time
        self.ratelimitsleep_maxsleeps = ratelimit_maxsleeps
        self.ratelimit_max = ratelimit_max
        self.ratelimit_within = ratelimit_within
        self.ratelimit_enabled = ratelimit_enabled
        self.xrls = 0
        self.rlobj = RateLimit()

    def rate_limit(self, new_xrls=1):
        # Raises an exception if RateLimit is either banned 
        self.xrls = int(new_xrls)
        self.rlobj.add_timestamp()

    def _check_ratelimit(self):
        return self.rlobj.ratelimitcheck(xrls=self.xrls,
                amount_allow=self.ratelimit_max,
                within_time=self.ratelimit_within)

    def check_ratelimit(self):
        rlflag = self.check_ratelimit()
        if not rlflag:
            if self.ratelimit_sleep:
                n = 0
                while self._check_ratelimit():
                    n = n + 1
                    if n >= self.ratelimit_maxsleeps:
                        break                        
                    sleep(self.ratelimitsleep_time)
                else:
                    return True
            raise RateLimitReached("The Rate Limit was too close the API limit to safely handle this request")
        else:
            return True

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
    	
    def Telegram(self, client_key=None, tgid=None, key=None):
        return TelegramAPI(self, client_key, tgid, key)