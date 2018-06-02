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

class NSBaseError(Exception):
	"""Base Error for all custom exceptions"""

	pass

class RateLimitReached(NSBaseError):
	"""Rate Limit was reached"""

class NSServerBaseException(NSBaseError):
    """Exceptions that the server returns"""
    pass

class APIError(NSServerBaseException):
    """General API Error"""
    pass

class Forbidden(APIError):
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
    def __init__(self, url, api_name, api_value, shards, version, custom_headers):
        self.url = url
        self.api_name = api_name
        self.api_value = api_value
        self.shards = shards
        self.version = version
        self.custom_headers = custom_headers

class NationstatesAPI:
    """Implements Generic Code that is used by Inherited
     Objects to use the API"""
    api_name = None

    def __init__(self, api_mother):

        self.api_mother = api_mother

    def _ratelimitcheck(self):
        rlflag = self.api_mother.rl_can_request()

    def _prepare_request(self, url, api_name, api_value, shards, version=None, request_headers=None):
        if request_headers is None:
            request_headers = dict()
        return APIRequest(url, api_name, api_value, shards, version, request_headers)

    def _request_api(self, req):
        sess = self.api_mother.session
        headers = {"User-Agent":self.api_mother.user_agent}
        headers.update(req.custom_headers)
        return sess.get(req.url, headers=headers)

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

    def _request(self, shards, url, api_name, value_name, version, request_headers=None):
    	# This relies on .url() being defined by child classes
        url = self.url(shards)
        req = self._prepare_request(url, 
                api_name,
                value_name,
                shards, version, request_headers)
        resp = self._request_api(req)
        result = self._handle_request(resp, req)
        return result


class NationAPI(NationstatesAPI):
    api_name = "nation"

    def __init__(self, nation_name, api_mother):
        self.nation_name = nation_name
        super().__init__(api_mother)

    def request(self, shards=[]):
        url = self.url(shards)
        return self._request(shards, url, self.api_name, self.nation_name, self.api_mother.version)

    def url(self, shards):
        return self._url(self.api_name, 
            self.nation_name,
            shards,
            self.api_mother.version)

class PrivateNationAPI(NationAPI):
    def __init__(self, nation_name, api_mother, password=None, autologin=None):
        self.password = password
        self.autologin = autologin
        if autologin:
            self.autologin_used = True
        else:
            self.autologin_used = False
        self.pin = None
        super().__init__(nation_name, api_mother)

    def request(self, shards=[], allow_sleep=False):

        pin_used = bool(self.pin)
        if self.pin:
            custom_headers={"Pin": self.pin}
        else:
            if self.autologin:
                custom_headers={"Autologin":self.autologin}
            elif self.password:
                custom_headers = {"Password": self.password}
        url = self.url(shards)
        try:
            response = self._request(shards, url, self.api_name, self.nation_name, self.api_mother.version, request_headers=custom_headers)
        except Forbidden:
            # PIN is wrong or login is wrong
            if pin_used:
                self.pin = None
                return self.request(self, shards, allow_sleep)
            else:
                raise Forbidden("Password or Autologin code was not correct, server returned 403")
        except ConflictError as exc:
            if allow_sleep:
                # sleep code
                pass
            else:
                raise exc
            
        self._setup_pin(response)
        return response

    def _setup_pin(self, response):
        # sets up pin
        if self.password or self.autologin or self.pin:
            headers = response["headers"]
            try:
                self.pin = headers["X-Pin"]
                self.autologin = headers["X-AutoLogin"]
                self.password = None
            except KeyError:
                # A Non Private Request was done
                # Nothing needs to be done
                pass

class RegionAPI: 
    api_name = "region"

    def __init__(self, nation_name, api_mother):
        self.nation_name = nation_name
        super().__init__(api_mother)

    def request(self, shards=[]):
        url = self.url(shards)
        return self._request(shards, url, self.api_name, self.nation_name, self.api_mother.version)

    def url(self, shards):
        return self._url(self.api_name, 
            self.nation_name,
            shards,
            self.api_mother.version)

class WorldAPI(NationstatesAPI): 
    api_name = "world"

    def __init__(self, api_mother):
        super().__init__(api_mother)

    def request(self, shards=[]):
        url = self.url(shards)
        return self._request(shards, url, self.api_name, None, self.api_mother.version)

    def url(self, shards):
        return self._url(self.api_name, 
            None,
            shards,
            self.api_mother.version)

class WorldAssembly(NationstatesAPI):
    api_name = "wa"

    def __init__(self, chamber, api_mother):
        self.chamber = api_mother

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

    def check_ratelimit(self):
        rlflag = self.rlobj.ratelimitcheck(xrls=self.xrls)
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
    	return WAAPI(chamber, self)

