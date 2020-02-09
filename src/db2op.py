import json
import kopf
import kubernetes
import yaml


NAMESPACE = 'db2'
DEPLOY_FILE = 'deployment.json'

@kopf.on.create('example.com', 'v1', 'db2claims')
def create_fn(body, **kwargs):
    # Create a container in our namespace (db2).
    # Name it according to the name on the db2c CRD.
    # Apply a from-namespace label to it, for informational purposes

    print(f"A handler is called with body: {body}")

    configuration = kubernetes.client.Configuration()
    api_instance = kubernetes.client.AppsV1Api(kubernetes.client.ApiClient(configuration))

    name = body['metadata']['name']
    new_body = json.load(open(DEPLOY_FILE, 'r'))
    new_body['metadata']['name'] = name
    new_body['metadata']['labels']['db2claim-source-namespace'] = body['metadata']['namespace']

    print(f'Creating "{name}" in namespace "{NAMESPACE}"')
    try:
        api_response = api_instance.create_namespaced_deployment(NAMESPACE, new_body)
    except kubernetes.client.rest.ApiException as e:
        print(f'API exception {e}')


@kopf.on.delete('example.com', 'v1', 'db2claims')
def delete_fn(**kwargs):
    # If this is a deletion for a DB2Claim CRD, delete the
    # corresponding container running in our protected db2
    # namespace

    name = kwargs['name']
    configuration = kubernetes.client.Configuration()
    api_instance = kubernetes.client.AppsV1Api(kubernetes.client.ApiClient(configuration))

    print(f'Deleting "{name}" in namespace "{NAMESPACE}"')
    try:
        api_response = api_instance.delete_namespaced_deployment(name, NAMESPACE, pretty='true')
    except kubernetes.client.rest.ApiException as e:
        print(f'API exception {e}')

