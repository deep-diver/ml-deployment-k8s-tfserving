import tensorflow as tf
import numpy
import json
from locust import HttpUser, task, constant

class ImgClssificationUser(HttpUser):
    wait_time = constant(1)

    headers = {"content-type": "application/json"}

    inputs = tf.keras.utils.load_img('./cat_224x224.jpeg')
    inputs = numpy.array(inputs)
    inputs = numpy.expand_dims(inputs, 0)

    data = json.dumps({"signature_name": "serving_default", "instances": inputs.tolist()})

    @task
    def predict(self):
        r = self.client.post("/v1/models/resnet:predict", data=self.data, headers=self.headers)