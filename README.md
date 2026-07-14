# Sistema de Facturación Serverless — AWS

API REST serverless para gestión de facturas, construida con Python y AWS.

## Arquitectura

API Gateway → Lambda → DynamoDB
↓
SQS → Lambda → S3



## Servicios AWS utilizados

| Servicio | Uso |
|---|---|
| API Gateway | Endpoints HTTP públicos |
| Lambda | Lógica de negocio (Python) |
| DynamoDB | Almacenamiento de facturas |
| SQS | Cola de procesamiento asíncrono |
| S3 | Archivo de facturas procesadas |

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/facturas` | Crear factura nueva |
| GET | `/facturas` | Listar todas las facturas |
| GET | `/facturas/{id}` | Consultar una factura |
| PUT | `/facturas/{id}/estado` | Actualizar estado |

## Ejemplo de uso

```bash
# Crear factura
curl -X POST https://TU-URL/facturas \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nombre": "Empresa XYZ",
    "cliente_email": "contacto@xyz.com",
    "concepto": "Servicios de desarrollo web",
    "monto": 25000
  }'

# Consultar factura
curl https://TU-URL/facturas/FAC-XXXXXXXX

#Estructura del proyecto
facturacion/
├── lambda_api.py          # Lambda: endpoints CRUD
├── lambda_procesador.py   # Lambda: procesamiento SQS → S3
└── README.md
