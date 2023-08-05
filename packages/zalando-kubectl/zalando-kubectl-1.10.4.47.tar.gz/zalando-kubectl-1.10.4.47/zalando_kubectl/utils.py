import zign.api


def auth_headers():
    token = zign.api.get_token('kubectl', ['uid'])
    return {'Authorization': 'Bearer {}'.format(token)}


def get_api_server_url(config):
    try:
        return config['api_server']
    except Exception:
        raise Exception("Unable to determine API server URL, please run zkubectl login")
