import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamo = boto3.resource("dynamodb")
tabla = dynamo.Table("facturas")
s3 = boto3.client("s3")

BUCKET = "marcela-aprendizaje-aws-2026"

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    for record in event["Records"]:
        data = json.loads(record["body"])
        factura_id = data["factura_id"]

        respuesta = tabla.get_item(Key={"factura_id": factura_id})
        factura = respuesta.get("Item")

        if not factura:
            print(f"Factura {factura_id} no encontrada")
            continue

        fecha_procesada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        tabla.update_item(
            Key={"factura_id": factura_id},
            UpdateExpression="SET #e = :estado, fecha_procesada = :fecha",
            ExpressionAttributeNames={"#e": "estado"},
            ExpressionAttributeValues={
                ":estado": "procesada",
                ":fecha": fecha_procesada
            }
        )

        factura["estado"] = "procesada"
        factura["fecha_procesada"] = fecha_procesada

        s3.put_object(
            Bucket=BUCKET,
            Key=f"facturas/{factura_id}.json",
            Body=json.dumps(factura, cls=DecimalEncoder, ensure_ascii=False),
            ContentType="application/json"
        )

        print(f"Factura {factura_id} procesada y guardada en S3")
