from requests import Session
from bs4 import BeautifulSoup
from urls import gen_url

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
    if data["status"] == 409:
        raise ConflictError("Nationstates API has returned a Conflict Error.")
    if data["status"] == 400:
        raise APIError(data["bs4"].h1.text)
    if data["status"] == 403:
        raise Forbidden(data["bs4"].h1.text)
    if data["status"] == 404:
        raise NotFound(data["bs4"].h1.text)
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
	"""Data Class for requests"""
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

	def _ratelimitcheck

	def _request(self, url):
		sess = self.api_mother.session

		return sess.get(url)


	def _handle_request(self, response, request_meta):
		result = {
			"response": response,
			"xml": response.text
			"bs4": BeautifulSoup(response.text, "lxml")
		}
		response_check(data)

		 return

		#xmltodict

	def _url(self, api_name, value, shards, version):
		return gen_url(
			api=(api_name, value), 
			shards=shards,
			version=version)


class Nation(NationstatesAPI):
	api_name = "nation"
	
	def __init__(self, nation_name, api_mother):
		self.nation_name = nation_name


	def url(self, shards):
		return self._url(self.api_name, 
			self.nation_name,
			shards,
			self.api_mother.version)

class Api:
	def __init__(self, user_agent, version="9"):
		self.user_agent = user_agent
		self.version = version
		self.session = Session()
		self.xlrs = 0

	def rate_limit(self, xlrs):
		# Raises an exception if RateLimit is either banned 
		pass