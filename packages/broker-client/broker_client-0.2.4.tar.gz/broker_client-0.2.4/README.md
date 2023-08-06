# Broker Client Module Repository


## Install

Install with `pip`: `pip install broker_client`


Or, put this on your `requirements.txt`:

```
broker_client
```

## Use

```
import broker_core

# then, if you are a service provider, register your service:
register("service-description-filename.jsonld")
# the response is a tuple, either:
#  (True, service_description_dict) for when the request worked, or
#  (False, service_description_dict) for when the request failed

# and if you want to discover a service of type FictionalType:
locate({"@type": "http://schema.org/FictionalType"}, "http://put-the-broker.url.here")
# the response is a list of the found service descriptions
```
