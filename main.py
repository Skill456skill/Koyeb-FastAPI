from typing import Union
from fastapi import FastAPI, Query

import mook
import re

import boto3
import uuid

aws_access_key_id = 'AKIAXII2BKO7JEZJAWWV'
aws_secret_access_key = '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'

sqs = boto3.client(
    'sqs',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
queue_url= 'https://sqs.us-east-1.amazonaws.com/498807690174/davivienda.fifo'

app = FastAPI()

def send(cantidad: int):
    # Publicar un mensaje en la cola
    for i in range(0, cantidad):
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody= f"Transaction {i}",
            MessageGroupId='pagos',
            MessageDeduplicationId=str(uuid.uuid4())
        )
        print(f"Enviando Transaction {i} - {response['MessageId']}")
    print(f'Mensaje publicado con éxito: {response["MessageId"]}')

def process():
    #Recibir mensajes de la cola
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'ALL'
        ],
        MessageAttributeNames=[
            'ALL'
        ],
        MaxNumberOfMessages=1,
        VisibilityTimeout=30,
        WaitTimeSeconds=0
    )
    
    print(response)
    if response.get('Messages'):
        message = response ['Messages']
        print("Mensaje recibido: (message [0] ['ReceiptHandle']}")

        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message[0]['ReceiptHandle']
        )
    else:
        print("No se encontraron mensajes en la cola.")
    sqs.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/data")
def read_item(data: str | None = Query(None, min_length=3)):
    return {"tutelas": data}

@app.get("/api/v1/search")
def read_item(tipo_tutela: str | None = Query(None, min_length=3)):
    result = []
    for tutela in mook.tutelas:
        if re.search(tipo_tutela, tutela["titulo"] + " " + tutela["resumen"], re.IGNORECASE):
            result.append(tutela)
    return result

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}