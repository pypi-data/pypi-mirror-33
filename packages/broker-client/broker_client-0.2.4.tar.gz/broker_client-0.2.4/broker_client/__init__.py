import requests
import socket
import json
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

def locate(query={"@type": "*"}, broker_url="http://localhost:4000/broker"):
    locate_url = broker_url + "/locate-requests"
    try:
        logging.info("Locating query %s" % query)
        response = requests.post(locate_url, data=json.dumps(query), headers={'Content-Type': 'application/json'})
        services = response.json()
        logging.info("Located services are %s" % list(map(lambda s: s["host"] + s["@id"], services)))
        return services
    except Exception as e:
        print("The locate request did not work")

def register(sd_filename="service-description.jsonld", replace_localhost_by_ip=True):
    sd = get_service_description(sd_filename)
    my_ip = find_my_ip()
    if replace_localhost_by_ip and my_ip:
        sd = sd.replace("localhost", my_ip)

    sd_json = json.loads(sd)
    registry_url = sd_json["broker"] + "/registry"
    try:
        requests.post(registry_url, data=sd, headers={'Content-Type': 'application/json'})
        logging.info("Registered service %s" % (sd_json["host"] + sd_json["@id"]))
        return (True, sd_json)
    except Exception as e:
        print("No available broker at localhost to register at")
        return (False, sd_json)

def get_service_description(filename="service-description.jsonld"):
    sd_file = open(filename, "r")
    sd = sd_file.read()
    sd_file.close()
    return sd

def find_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = None
    finally:
        s.close()
    return ip

