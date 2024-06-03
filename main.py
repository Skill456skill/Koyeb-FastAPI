from typing import Union
from fastapi import FastAPI, Query

import mock
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


# Tutelas --> Filtro 

def buscador():
    indices = {}
    filter = ["violencia", "medicinas", "fly", "Outside"]
    for tutela in mock.tutela:
        words = tutela["resumen"].split()
        for word in words:
            if word in filter:
                if word in indices:
                    indices[word].append(tutela)
                else:
                    indices[word] = [tutela]
    return indices

@app.get("/")
def read_root():
    return {"!Hello, Welcome to this Webside! \n"
            +"\nHere, you must put on these command to surf: \n"
            +"- /docs"}



@app.get("/search")
def read_item(palabra:str):

    index = buscador()

    return {"tutelas encontradas": index.get(palabra "\n\n", "no encontrado")}

