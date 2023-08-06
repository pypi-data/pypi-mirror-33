import logging
import time
import grpc
from grpc import RpcError

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2
from tensorflow.contrib.util import make_tensor_proto


class PredictClient:

    def __init__(self, host_port):

        self.logger = logging.getLogger(self.__class__.__name__)  # naming logger with class name
        self.host_port = host_port

    def predict(self, request_data, model_name, model_version, signature_name='', request_timeout=5):
        """
        :param request_data:
        :param model_name:
        :param model_version:
        :param signature_name:
        :param request_timeout:
        :return:
        """

        self.logger.info('Sending request to the model')
        self.logger.info('HOST: {} / PORT: {}'.format(self.host_port.split(":")[0], self.host_port.split(":")[-1]))
        self.logger.info('MODEL: {}'.format(model_name))
        self.logger.info('MODEL VERSION: {}'.format(model_version))

        # Create the connection
        # ---------------------------------------------------

        # Create the channel
        channel_time = time.time()
        channel = grpc.insecure_channel(self.host_port)
        self.logger.debug('Establishing insecure channel during {}'.format(time.time()-channel_time))

        # Create Stub
        stub_time = time.time()
        stub = prediction_service_pb2.PredictionServiceStub(channel)
        self.logger.debug('Creating stub during {}'.format(time.time()-stub_time))

        # Initialise a request
        # ---------------------------------------------------
        request_time = time.time()
        request = predict_pb2.PredictRequest()
        self.logger.debug('Creating request during {}'.format(time.time()-request_time))

        # Specify request arguments
        # ---------------------------------------------------
        request.model_spec.name = model_name

        if type(model_version) == int and model_version > 0:
            request.model_spec.version.value = model_version

        if signature_name != '':
            request.model_spec.signature_name = signature_name

        # Set inputs
        # ---------------------------------------------------
        input_time = time.time()
        for field in request_data:
            tensor_proto = make_tensor_proto(field['data'], field['dtype'])
            request.inputs[field['tensor_name']].CopyFrom(tensor_proto)

        self.logger.debug('Making tensor protos during {}'.format(time.time()-input_time))

        # Send the request
        # ---------------------------------------------------

        try:
            send_request_time = time.time()
            predict_response = stub.Predict(request, timeout=request_timeout)

            self.logger.debug('Time to get response: {}'.format(time.time()-send_request_time))

            return predict_response

        except RpcError as e:
            self.logger.error(e)
            self.logger.error('Prediction failed!')
            return {"error": "request failed!"}

        return {}





