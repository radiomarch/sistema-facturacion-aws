import json
import boto3
import os
from datetime import datetime
import uuid
from decimal import Decimal

dynamo = boto3.resource("dynamodb")
tabla = dynamo.Table("facturas")
sqs = boto3.client("sqs")

QUEUE_URL = os.environ["COLA_FACTURAS_URL"]

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def responder(status, data):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS"
        },
        "body": json.dumps(data, cls=DecimalEncoder, ensure_ascii=False)
    }


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path = event["requestContext"]["http"]["path"]
    
    if method == "OPTIONS":
        return responder(200, "OK")
     try:
        if method == "POST" and path == "/facturas":
            return crear_factura(event)
        elif method == "GET" and path == "/facturas":
            return listar_facturas()
        elif method == "GET":
            return obtener_factura(event["pathParameters"]["id"])
        elif method == "PUT":
            return actualizar_estado(event, event["pathParameters"]["id"])
        else:
            return responder(404, "Ruta no encontrada")
    except Exception as e:
        return responder(500, f"Error interno: {str(e)}")

def crear_factura(event):
    data = json.loads(event["body"])

    for campo in ["cliente_nombre", "cliente_email", "concepto", "monto"]:
        if not data.get(campo):
            return responder(400, f"Campo requerido: {campo}")

    factura_id = f"FAC-{uuid.uuid4().hex[:8].upper()}"

    factura = {
        "factura_id": factura_id,
        "cliente_nombre": data["cliente_nombre"],
        "cliente_email": data["cliente_email"],
        "concepto": data["concepto"],
        "monto": Decimal(str(data["monto"])),
        "estado": "pendiente",
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
    }

    tabla.put_item(Item=factura)

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({"factura_id": factura_id})
    )

    return responder(201, {
        "mensaje": "Factura creada correctamente",
        "factura_id": factura_id,
        "estado": "pendiente"
    })

def obtener_factura(factura_id):
    respuesta = tabla.get_item(Key={"factura_id": factura_id})
    item = respuesta.get("Item")

    if not item:
        return responder(404, f"Factura {factura_id} no encontrada")

    return responder(200, item)

def listar_facturas():
    respuesta = tabla.scan()
    facturas = respuesta.get("Items", [])
    return responder(200, {"total": len(facturas), "facturas": facturas})

def actualizar_estado(event, factura_id):
    data = json.loads(event["body"])
    nuevo_estado = data.get("estado")

    if nuevo_estado not in ["pendiente", "procesada", "cancelada"]:
        return responder(400, "Estado inválido. Opciones: pendiente, procesada, cancelada")

    if not tabla.get_item(Key={"factura_id": factura_id}).get("Item"):
        return responder(404, f"Factura {factura_id} no encontrada")

    tabla.update_item(
        Key={"factura_id": factura_id},
        UpdateExpression="SET #e = :estado",
        ExpressionAttributeNames={"#e": "estado"},
        ExpressionAttributeValues={":estado": nuevo_estado}
    )

    return responder(200, {
        "mensaje": f"Estado actualizado a '{nuevo_estado}'",
        "factura_id": factura_id
    })
