from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import uuid
import random

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "[ENDPOINT]"
CLIENT_ID = "Sensor"
PATH_TO_CERTIFICATE = "certificates/certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certificates/private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certificates/root.pem"
myAWSIoTMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

list_topic = ['iot-device/sensor1', 'iot-device/sensor2']

def create_payload():
    TOPIC = random.choice(list_topic)
    payload = json.dumps({
        "id": str(uuid.uuid4()),
        "read_date": int(time.time()),
        "topic": TOPIC,
        "humidity": random.randint(70,90),
        "temperature": random.randint(15,35)
    })
    return payload, TOPIC

myAWSIoTMQTTClient.connect()
print('Begin Publish')
while True:
    message, TOPIC = create_payload()
    myAWSIoTMQTTClient.publish(TOPIC, message, 1) 
    print("Published: '" + message + "' to the topic: " + TOPIC)
    time.sleep(1)
print('Publish End')
myAWSIoTMQTTClient.disconnect()