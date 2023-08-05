# Install

    pip install trackely_client

# Usage

    from trackely_client.api import APIClient

    client = APIClient('KEY', 'SECRET')
    response = create_campaign('My first campaign')
    # {
    # 	'success': True,
    #   'campaign': {
    #		'id': 'ABC'
	#   }
	# }


# Available methods

* create_campaign
* create_ad
* create_pixel

