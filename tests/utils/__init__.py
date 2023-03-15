from .config import test_config


def get_specific_url(path):
    bistro_address = test_config['bistro']['url']
    return '{}{}'.format(bistro_address, path)


LOGIN_URL = get_specific_url('fe-apps/auth/login')
AUTH_URL = get_specific_url('auth/me/')
DASHBOARD_URL = get_specific_url('fe-apps/dashboard')
