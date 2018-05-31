from requests import Session
from bs4 import BeautifulSoup
from urls import gen_url, Shard
from time import time as timestamp

class RateLimit:

    """
    This object wraps around the ratelimiting system. 

    """
    def __init__(self):
        self.rlref = []

    @property
    def rltime(self):
        """Returns the current tracker"""
        return self.rlref

    @rltime.setter
    def rltime(self, val):
        """Sets the current tracker"""
        self.rlref = val

    def ratelimitcheck(self, amount_allow=48, within_time=30, xrls=0):
        """Checks if PyNationstates needs pause to prevent api banning"""

        if xrls >= amount_allow:
            pre_raf = xrls - (xrls - len(self.rltime))
            currenttime = timestamp()
            try:
                while (self.rltime[-1]+within_time) < currenttime:
                    del self.rltime[-1]
                post_raf = xrls - (xrls - len(self.rltime))
                diff = pre_raf - post_raf
                nxrls = xrls - diff
                if nxrls >= amount_allow:
                    return False
                else:
                    return True
            except IndexError as err:
                if (xrls - pre_raf) >= amount_allow:
                    return False
                else:
                    return True
        else:
            self.cleanup()
            return True

    def cleanup(self, amount_allow=50, within_time=30):
        """To prevent the list from growing forever when there isn't enough requests to force it
            cleanup"""
        try:
            currenttime = timestamp()
            while (self.rltime[-1]+within_time) < currenttime:
                del self.rltime[-1]
        except IndexError as err:
            #List is empty, pass
            pass


    def add_timestamp(self):
        """Adds timestamp to rltime"""
        self.rltime = [timestamp()] + self.rltime


class NSServerBaseException(Exception):
    """Exceptions that the server returns"""
    pass

class APIError(NSServerBaseException):
    """General API Error"""
    pass

class ConflictError(APIError):
    """ConflictError from Server"""
    pass

class NotFound(APIError):
    """Nation/Region Not Found"""
    pass

class APIRateLimitBan(APIError):
    """Server has banned your IP"""
    pass

def response_check(data):

    xmlsoup = BeautifulSoup(data["xml"], "lxml")
    if data["status"] == 409:
        raise ConflictError("Nationstates API has returned a Conflict Error.")
    if data["status"] == 400:
        raise APIError(xmlsoup.h1.text)
    if data["status"] == 403:
        raise Forbidden(xmlsoup.h1.text)
    if data["status"] == 404:
        raise NotFound(xmlsoup.h1.text)
    if data["status"] == 429:
        message = (
            "Nationstates API has temporary banned this IP for Breaking the Rate Limit. Retry-After: {seconds}"
                    .format(
                       seconds=(data["response"]
                                .headers["X-Retry-After"])))
        raise APIRateLimitBan(message)
    if data["status"] == 500:
        message = ("Nationstates API has returned a Internal Server Error")
        raise APIError(message)
    if data["status"] == 521:
        raise APIError(
            "Error 521: Cloudflare did not recieve a response from nationstates"
            )

class APIRequest:
    """Data Class for this library"""
    def __init__(self, url, api_name, shards, version):
        self.url = url
        self.api_name = api_name
        self.shards = shards
        self.version = version

class NationstatesAPI:
    """Implements Generic Code that is used by Inherited
     Objects to use the API"""
    api_name = None

    def __init__(self, api_mother):

        self.api_mother = api_mother

    def _ratelimitcheck(self):
        rlflag = self.api_mother.rl_can_request()

    def _prepare_request(self, url, api_name, shards, version):
        return APIRequest(url, api_name, shards, version)

    def _request(self, req):

        sess = self.api_mother.session

        return sess.get(req.url)

    def _handle_request(self, response, request_meta):
        result = {
            "response": response,
            "xml": response.text,
            "request": request_meta,
            "status": response.status_code,
            "headers": response.headers,
        }
        # Should this be here? Perhaps an argument
        response_check(result)
        self.api_mother.rate_limit(new_xrls=response.headers["X-ratelimit-requests-seen"])

        return result

    def _url(self, api_name, value, shards, version):
        return gen_url(
            api=(api_name, value), 
            shards=shards,
            version=version)


class Nation(NationstatesAPI):
    api_name = "nation"

    def __init__(self, nation_name, api_mother):
        self.nation_name = nation_name
        super().__init__(api_mother)

    def request(self, shards=[]):
        url = self.url(shards)
        req = self._prepare_request(url, 
                self.api_name,
                self.nation_name,
                shards)
        resp = self._request(req)
        result = self._handle_request(resp, req)
        return result

    def url(self, shards):
        return self._url(self.api_name, 
            self.nation_name,
            shards,
            self.api_mother.version)

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
        self.xrls = new_xrls
        self.rlobj.add_timestamp()

    def rl_can_request(self):
        return self.ratelimitcheck(xrls=self.xlrs)

    def Nation(self, name):
        return Nation(name, self)

    def Region(self):
        pass

    def World(self):
        pass

test = Api("NATIONSTATES API WRAPPER V2 Dev: The United Island Tribes")

n = test.Nation("The United Island Tribes")
for row in range(5):
    n.request()
    print(test.xrls)
    print(test.rlobj.rltime)