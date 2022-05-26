import grpc
import numpy as np
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc

image = tf.image.decode_jpeg(tf.io.read_file("../cat_224x224.jpg"))
# uncomment below if you want to preprociess on client side
# image = tf.image.resize(image, (224, 224))[None, ...]

# $ENDPOINT from LoadBalancer or Ingress
channel = grpc.insecure_channel("$ENDPOINT:8500")
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

request = predict_pb2.PredictRequest()
request.model_spec.name = "$MODEL_NAME"
request.model_spec.signature_name = "serving_default"
request.inputs["image_input"].CopyFrom(tf.make_tensor_proto(image))

grpc_predictions = stub.Predict(request, 25.0)

# $MODEL_OUT is set "resnet50" in standard Keras resnet50 model
grpc_predictions = grpc_predictions.outputs["$MODEL_OUT"].float_val
grpc_predictions = np.array(grpc_predictions).reshape(1, -1)

print("Prediction class: {}".format(np.argmax(grpc_predictions, axis=-1)))