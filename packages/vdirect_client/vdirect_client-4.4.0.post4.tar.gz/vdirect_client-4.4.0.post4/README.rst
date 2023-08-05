.. image:: http://www.radappliances.com/images/Software/vDirect/vdirect.jpg

============================================================
A REST-based python client for Radware vDirect
============================================================
An auto-generated REST-based client for `Radware vDirect <https://www.radware.com/products/vdirect/>`_


*******************
Client features:
*******************
- Supports asynchronous mode. The default behavior of the client is to wait for completion of the requested operation. This behavior can be overidden. See the FAQ section at the end of this file for more details.
- Supports vDirect server HA. When configured with a secondary vDirect IP address, the client automatically tries to switch to the secondary vDirect server instance when the primary vDirect server is not available.

- API call result is a tuple with four entries:
    * Entry 1 is an HTTP response code. For example: 404 (int)
    * Entry 2 is an HTTP response reason. For example: Not found. (string)
    * Entry 3 is the response as a string.
    * Entry 4 is usually the response as a dict or a list of dicts.

To understand which payloads to send and their expected response, developers should consult the vDirect REST API documentation at https://<vdirect server IP address>:2189/docs/api-docs/.


*******************
Basic client usage:
*******************
.. code-block:: python

    from vdirect_client import rest_client
    from vdirect_client.rest_client import RestClient

    def show(result):
        print result[rest_client.RESP_STATUS]
        print result[rest_client.RESP_REASON]
        print result[rest_client.RESP_STR]
        print result[rest_client.RESP_DATA]

    ip = <vDirect server IP address>
    user = <vDirect server user name>
    password = <vDirect server password>

    client = RestClient(ip, user, password)
    data = {"tenants":[],"parameters":{"vipAddress":"1.1.1.1","ServerIps":["1.2.3.4","1.2.3.5"]},
                                       "devices":{"adc":{"deviceId":{"name":"Site1.vx2"}}}}
    show(client.runnable.run(data,'ConfigurationTemplate','caching_enh','run'))
    show(client.ha.get_ha_config())
    show(client.ha.get_ha_status())
    show(client.template.list())
    show(client.defensePro.list())

	
*******************
FAQ:
*******************
:Q: What do RestClient init parameters mean?
:A: RestClient init parameters description:

* vdirect_ip: The primary / standalone vDirect server IP address (string)
* vdirect_user: The vDirect server user name (string)
* vdirect_password: The vDirect server user password (string)
* wait: Wait for asynchronous operations to complete (boolean). Default is True
* secondary_vdirect_ip: The secondary vDirect server IP address (string). Relevant for vDirect server HA pair
* https_port: The https vDirect server port. Default is 2189 (integer)
* http_port: The http vDirect server port. Default is 2188 (integer)
* timeout: Time period (seconds) to wait for asynchronous operations completion (integer). Relevant for case where "wait" parameter is set to True. Default is 60 seconds
* https: Use HTTPS connections (boolean), Default is True
* strict_http_results: If set to True, only accept success HTTP status codes and throw exception for 4xx and 5xx status codes. Default is False
* verify: Verify SSL certificates on HTTPS connections (boolean). Default is True
* fetch_result: Fetch the result automatically if resultUri exists in response (boolean). Default is False

:Q: How can I use vdirect_client in several places without passing init paramters each time?
:A: You can use environment variables instead of any RestClient init parameter. Following is a map of init parameters and their respective environment variable names:

* vdirect_ip - VDIRECT_IP
* vdirect_user - VDIRECT_USER
* vdirect_password - VDIRECT_PASSWORD
* wait = VDIRECT_WAIT
* secondary_vdirect_ip - VDIRECT_SECONDARY_IP
* https_port - VDIRECT_HTTPS_PORT
* http_port - VDIRECT_HTTP_PORT
* timeout - VDIRECT_TIMEOUT
* https - VDIRECT_HTTPS
* strict_http_results- VDIRECT_STRICT_HTTP_RESULT
* verify - VDIRECT_VERIFY
* fetch_result - VDIRECT_FETCH_RESULT

:Q: How do I disable SSL certificates verification on HTTPS connection?
:A: To disable SSL certificates verification, do one of the following: either set the RestClient init "verify" parameter to False, or set environment variable VDIRECT_VERIFY to False.

:Q: Why do I see method names ending with numbers, e.g. "create0", "list2", "acquire0", and others?
:A: vdirect_client code is a generated code and those method names are the result of technical constraints.

:Q: How do I know if my asynchronous operation has completed and succeeded?
:A: See the vDirect REST API documentation at https://<vdirect server IP address>:2189/docs/api-docs/async.html.

:Q: What is the difference between synchronous and asynchronous modes?
:A: See the vDirect REST API documentation at https://<vdirect server IP address>:2189/docs/api-docs/async.html.
    Following is a python code sample demonstrating how to get the URI token from the operation response, and to periodically verify whether the operation has completed, and if completion was successful.

.. code-block:: python
	
    import json
    import requests
    import time
		
    from vdirect_client import rest_client
    from vdirect_client.rest_client import RestClient

    ip = <vDirect server IP address>
    user = <vDirect server user name>
    password = <vDirect server password>

    # creating rest client with wait parameter set to False 
    client = RestClient(ip, user, password, wait=False)
    data = {"tenants":[],"parameters":{"vipAddress":"1.1.1.1","ServerIps":["1.2.3.4","1.2.3.5"]},
                                       "devices":{"adc":{"deviceId":{"name":"Site1.vx2"}}}}
    # Requesting operation and getting the operation URI token for completion sampling
    ret = client.runnable.run(data,'WorkflowTemplate','caching_enh','createWorkflow')
    token_uri = ret[rest_client.RESP_DATA]['uri']

    # Getting the URI and periodically check for completion and success
    cntr = 0
    timeout = 10
    while cntr < timeout:
        time.sleep(1)
        cntr+= 1
        ret = requests.get(token_uri, auth=(user, password), verify=False)
        content = json.loads(ret.content)
        if content['complete']:
            break

    if content['complete']:
        print("Operation completed")
        if (content['success']):
            print("Operation succeeded")
        else:
            print("Operation failed")
    else:
        print("Operation not completed")
		

:Q: What is vDirect HA and how does it work?
:A: vdirect_client supports vDirect server HA mode. For further information, see the vDirect documentation at https://<vdirect server IP address>:2189/docs/api-docs/examples/haServer/index.html.