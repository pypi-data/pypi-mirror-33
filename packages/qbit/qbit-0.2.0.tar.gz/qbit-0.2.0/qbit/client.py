import grpc
import json
import time
import requests
import qbit_pb2_grpc

from google.protobuf.json_format import MessageToDict


def create_get_auth(access_token):

    def get_auth_token(context, callback):
        callback([('authorization', access_token)], None)

    return get_auth_token

# Client class takes care of authentication process in order to use our services
#
# Example -
# from qbit import client
# qbit_client = client('./qbit/license.json')
# qbit_client.stub has all the grpc functions 1qbit has
class qloud_grpc_client(object):

    def __init__(self,
                 root_certs,
                 auth_url,
                 host,
                 client_id=None,
                 client_secret=None):
        channel_creds = grpc.ssl_channel_credentials(
            root_certificates=root_certs)

        # we still want user to create stub without authentication token
        if client_id and client_secret:
            req_dict = {
                "client_id": client_id,
                "client_secret": client_secret
            }

            try:
                response = requests.post(auth_url, json=req_dict)
                if response.ok:
                    response_data = response.json()
                    token = response_data["token"]
                else:
                    raise Exception(response.reason
                        + " ("
                        + str(response.status_code)
                        + ")")
            except Exception as e:
                raise Exception("Requesting Authentication Failed: " +  e.message)

            auth_creds = grpc.metadata_call_credentials(create_get_auth(token))
            channel_creds = grpc.composite_channel_credentials(
                channel_creds, auth_creds)

        self.channel = grpc.secure_channel(host, channel_creds)
        self.stub = qbit_pb2_grpc.QbitStub(self.channel)

def client(root_certs,
           auth_url="https://api.1qbit.com/v1/get_project_token",
           host='grpc.1qb.it',
           client_id=None,
           client_secret=None):
    return qloud_grpc_client(root_certs, auth_url, host, client_id, client_secret).stub
