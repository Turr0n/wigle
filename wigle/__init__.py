import requests

WIGLE_ENDPOINT = 'https://api.wigle.net/api/v2'

# How many entries will be sent from the server at one time. This is hardcoded
# on the website.
WIGLE_PAGESIZE = 100


def normalise_entry(net):
    net['trilat'] = float(net['trilat'])
    net['trilong'] = float(net['trilong'])


class WigleError(Exception):
    pass


class WigleAuthenticationError(WigleError):
    """
    Incorrect credentials.
    """
    pass


class WigleRequestFailure(WigleError):
    """
    Generic "request unsuccessful" error.
    """
    pass


class WigleRatelimitExceeded(WigleRequestFailure):
    """
    Too many requests have been made in a short time.
    """
    pass


def raise_wigle_error(data):
    message = data.get('message')
    if message == "too many queries":
        raise WigleRatelimitExceeded()
    else:
        raise WigleRequestFailure(message)


class Wigle(object):
    def __init__(self, name, token):
        """
        Create a new webservice proxy object. It will authenticate with user
        and password credentials on the first connection attempt.
        """
        self.auth = requests.auth.HTTPBasicAuth(name, token)

    def _wigle_request(self, method, isPOST=True, **kwargs):
        url = WIGLE_ENDPOINT + '/' + method
        headers = {
            'Accept': 'application/json, text/javascript',
            'User-Agent': 'python wigle client',
            'Content-Type': 'application/x-www-form-urlencoded;',
            }
        if (isPOST):
            return requests.post(url, headers=headers, auth=self.auth, **kwargs)
        else:
            return requests.get(url, headers=headers, auth=self.auth, **kwargs)

    def get_user_info(self):
        """
        Request information about current user.

        Returns:
            dict: Description of user.
        """
        resp = self._wigle_request('profile/user', isPOST=False)
        info = resp.json()
        return info

    def search(self, lat_range=None, long_range=None, variance=None,
               bssid=None, ssid=None,
               last_update=None,
               address=None, state=None, zipcode=None,
               on_new_page=None, max_results=100):
        """
        Search the Wigle wifi database for matching entries. The following
        criteria are supported:

        Args:
            lat_range ((float, float)): latitude range
            long_range ((float, float)): longitude range
            variance (float): radius tolerance in degrees
            bssid (str): BSSID/MAC of AP
            ssid (str): SSID of network
            last_update (datetime): when was the AP last seen
            address (str): location, address
            state (str): location, state
            zipcode (str): location, zip code
            on_new_page (func(int)): callback to notify when requesting new
                page of results

        Returns:
            [dict]: list of dicts describing matching wifis
        """
        params = {
            'latrange1': lat_range[0] if lat_range else "",
            'latrange2': lat_range[1] if lat_range else "",
            'longrange1': long_range[0] if long_range else "",
            'longrange2': long_range[1] if long_range else "",
            'variance': str(variance) if variance else "0.01",
            'netid': bssid or "",
            'ssid': ssid or "",
            'lastupdt': last_update.strftime("%Y%m%d%H%M%S") if last_update else "",
            'addresscode': address or "",
            'statecode': state or "",
            'zipcode': zipcode or "",
            'Query': "Query",
        }

        wifis = []
        while True:
            if on_new_page:
                on_new_page(params.get('first', 1))
            resp = self._wigle_request('network/search', isPOST=False, params=params)
            data = resp.json()
            if not data['success']:
                raise_wigle_error(data)

            for result in data['results'][:max_results-len(wifis)]:
                normalise_entry(result)
                wifis.append(result)

            if data['resultCount'] < WIGLE_PAGESIZE or len(wifis) >= max_results:
                break

            params['first'] = data['last'] + 1

        return wifis
