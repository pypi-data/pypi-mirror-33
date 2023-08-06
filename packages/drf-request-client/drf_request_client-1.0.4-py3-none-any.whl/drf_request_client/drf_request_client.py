import requests
# import logging


class MissingIDParameter(Exception):
  def __init__(self,):
    Exception.__init__(self, 'The \'id\' parameter must be included in the request')


class InvalidBaseUrl(Exception):
  def __init__(self,):
    Exception.__init__(self, 'The supplied base URL is not a valid string')


class InvalidToken(Exception):
  def __init__(self,):
    Exception.__init__(self, 'The supplied API token is not a valid string')

class DRFClient:
  def __init__(self, base_url, token):

    if type(base_url) != str or (not bool(base_url)):  # If the base_url is an empty string or None type
      raise InvalidBaseUrl

    if type(token) != str or (not bool(token)):
      raise InvalidToken

    self.requests = ApiRequest(base_url, token)
    self.client = Stage(requester=self.requests)


class ApiRequest:
  def __init__(self, base_url, token):
    self.base_url = base_url
    self.headers = {'Authorization': str(token)}

  def return_response(self, request_response):
    try:
      response = {'status_code': request_response.status_code, 'response': request_response.json()}
    except:
      response = {'status_code': request_response.status_code, 'response': {'text_response': request_response.text}}
    return response

  def get_request(self, request_url):
    # print(self.base_url + request_url)
    r = requests.get(self.base_url + str(request_url), headers=self.headers)
    return self.return_response(r)

  def post_request(self, request_url, data):
    # print(self.base_url + request_url)
    r = requests.post(self.base_url + str(request_url), json=data, headers=self.headers)
    return self.return_response(r)

  def put_request(self, request_url, data):
    r = requests.put(self.base_url + str(request_url), json=data, headers=self.headers)
    return self.return_response(r)

  def patch_request(self, request_url, data):
    r = requests.patch(self.base_url + str(request_url), json=data, headers=self.headers)
    return self.return_response(r)

  def delete_request(self, request_url):
    r = requests.delete(self.base_url + str(request_url), headers=self.headers)
    return self.return_response(r)


class Stage:
  def __init__(self, requester=None, path=None):
    self.path = path
    self.requester = requester

  def __getattr__(self, path):
    self.path = path
    return self.request

  def request(self, *args, **kwargs):
    request_url = '/{}/'.format(self.path.split('_')[0])

    # Determine the request type (currently based on DRF format)
    # -------------------------------------------------------------------------

    if self.path.endswith('_list'):
      separator = '?'
      for key in kwargs:
        request_url += '{}{}={}'.format(separator, key, kwargs[key])
        if separator == '?':
          separator = '&'
      return self.requester.get_request(request_url)

    elif self.path.endswith('_read'):
      if 'id' not in kwargs:
        raise MissingIDParameter
      request_url += str(kwargs['id']) + '/'
      return self.requester.get_request(request_url)

    elif self.path.endswith('_create'):
      return self.requester.post_request(request_url, kwargs)

    elif self.path.endswith('_partial_update'):
      if 'id' not in kwargs:
        raise MissingIDParameter
      request_url += str(kwargs['id']) + '/'
      return self.requester.patch_request(request_url, kwargs)

    elif self.path.endswith('_update'):
      if 'id' not in kwargs:
        raise MissingIDParameter
      request_url += str(kwargs['id']) + '/'
      return self.requester.put_request(request_url, kwargs)

    elif self.path.endswith('_delete'):
      if 'id' not in kwargs:
        raise MissingIDParameter
      request_url += str(kwargs['id']) + '/'
      return self.requester.delete_request(request_url)

    # Dealing with custom (non-DRF) requests. THIS MAY CHANGE IN THE FUTURE
    root_url = self.path.split('_')[0]
    request_url += self.path.replace(root_url, '', 1)[1:] + '/'

    if ('id' in kwargs and len(kwargs) == 1) or len(kwargs) == 0:  # A custom GET request (optionally) with an ID field
      if 'id' in kwargs:
        request_url += str(kwargs['id']) + '/'
      return self.requester.get_request(request_url)

    elif len(kwargs) >= 1:  # A custom POST request
      return self.requester.post_request(request_url, kwargs)

    else:
      raise Exception('Unknown request type')
