"""
Initial setup for the lights on a particular device
"""
import requests

LIGHT_TYPE = 'urn:schemas-upnp-org:device:BinaryLight:1'
DISCOVERY_URL = 'http://{}/data_request?id=user_data'
ACTION_URL = 'http://{url}/data_request?id=action&output_format=json&DeviceNum={device_num}' \
             '&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue={target_value}'
STATUS_URL = 'http://{url}/data_request?id=status&output_format=json&DeviceNum={device_num}'


def find_lights(url):
    """
    For the url, find all the 'Binary Lights' on the network
    :param url:
    :return:
    """
    lights = []
    resp = requests.get(DISCOVERY_URL.format(url))
    resp.raise_for_status()
    response = resp.json()

    for device in response['devices']:
        if device['device_type'] == LIGHT_TYPE:
            new_light = NexusLight(device['id'], name=device['name'], base_url=url)
            lights.append(new_light)

    return lights


class LightHub(object):
    """
    Establish a collection of turn-on-able lights on the network
    """
    def __init__(self, url):
        self.lights = find_lights(url)


class NexusLight(object):
    """
    Represents a nexus nero light
    """
    def __init__(self, device_num, name, base_url):
        self.status_url = STATUS_URL.format(url=base_url, device_num=device_num)
        self.action_url = ACTION_URL.format(url=base_url, device_num=device_num, target_value=0)
        self.device_num = device_num
        self.name = name

    @property
    def current_status(self):
        """ Get the current status of the light"""
        resp = requests.get(self.status_url)
        resp.raise_for_status()
        return check_is_on(resp.json(), self.device_num)

    def turn_on(self):
        """ Turn on a light"""
        resp = requests.post(self.action_url.format(target_value=1))
        resp.raise_for_status()

        light_response = resp.json()
        if light_response.get('u:SetTargetResponse'):
            return True
        return False

    def turn_off(self):
        """ Turn off a light"""
        resp = requests.post(self.action_url.format(target_value=0))
        resp.raise_for_status()

        light_response = resp.json()
        if light_response.get('u:SetTargetResponse'):
            return True
        return False


def check_is_on(json, id):
    """
    For a given json response from the light,
    check that it is on. For the zwave this isnt so
    easy - so we need to check if the bulb is using power
    :param json:
    :param id:
    :return:
    """
    for state in json['Device_Num_{}'.format(id)]['states']:
        if state['service'] == 'urn:micasaverde-com:serviceId:EnergyMetering1' and state['variable'] == "Watts":
            if float(state['value']) > 0.0:
                return True
            return False
