# About this fork

This project was abandoned 2 years ago and I needed this for some demo so i fixed the code to work with the new wigle API V2. It's a quick hack so it may breaks.

# Wigle

Python interface to wigle APIs. This project is unofficial and may stop working
due to API changes at any point without warning.

Currently supported operations: authentication, search and user information

# Search

Search supports all the options available via web interface. For example to
search for APs advertising network "foobar", use:

    wigle = Wigle('username', 'password')
    wigle.search(ssid="foobar")

Paging happens behind the scenes and will pull all results in multiple requests
when necessary (when `max_results` is set to value higher than 100).

See docstrings for more details.

# Command line tools

Search and user info are exposed as CLI tools `wigle_user_info` and
`wigle_search`.
