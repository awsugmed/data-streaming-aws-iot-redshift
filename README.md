# Requerimientos

## Opcion 1

- AWS Cloud9

## Opcion 2

- AWS Cli v2
- Python

# Instrucciones

## Descargar el certificado de la entidad certificadora

```sh
mkdir certificates
wget -O certificates/root1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
```

## Creación del certificado para los dispositivos IOT

```sh
aws iot create-keys-and-certificate \
--set-as-active \
--certificate-pem-outfile certificates/certificate.pem.crt \
--public-key-outfile certificates/public.pem.key \
--private-key-outfile certificates/private.pem.key 
```

> Nota: debe copiar el valor del parámetro `certificateArn` el cual se utilizará en el siguiente paso.

## Despliegue de servicios con Cloudformation

> Nota: se debe reemplazar `[CERTIFICATE_ARN]` por el valor copiado del paso anterior.

```sh
aws cloudformation deploy \
--template-file template.yaml \
--stack-name redshift-serverless \
--capabilities CAPABILITY_NAMED_IAM \
--parameter-overrides CertificateARN=[CERTIFICATE_ARN]
```

Ejemplo:

```sh
aws cloudformation deploy \
--template-file template.yaml \
--stack-name redshift-serverless \
--capabilities CAPABILITY_NAMED_IAM \
--parameter-overrides CertificateARN=arn:aws:iot:us-east-1:12348321861:cert/72eb1890d0291d3abca916b7957595ea220af080227db4bf3720b9827ee4ec01
```

## Generar datos de prueba en IoT Core

Obtener el endpoint de IoT Core

```sh
aws iot describe-endpoint
```

> Nota: se debe editar el archivo `publish_to_IoT.py` y cambiar `[ENDPOINT]` por el obtenido en el paso anterior.

Al ejecutar se genera una publicación por parte del sensor cada 1 segundo.

```sh
python publish_to_IoT.py
```

## Redshift Serverless

Crear un external schema para acceder a los datos de kinesis desde redshift

```sql
CREATE EXTERNAL SCHEMA kinesisdatastream
FROM kinesis
IAM_ROLE 'arn:aws:iam::12348321861:role/RedshiftKinesisRoleLab';
```

Se crea la vista materializada a partir de los datos capturados por Kinesis

```sql
CREATE MATERIALIZED VIEW v_streamlab AS
    SELECT approximatearrivaltimestamp,
    partitionkey,
    shardid,
    sequencenumber,
    json_parse(from_varbyte(data, 'utf-8')) as payload    
    FROM kinesisdatastream.streamlab;
```

Inicialmente la vista materializada no contiene datos, se debe refrescar manualmente para llevar los datos de Kinesis a Redshift. Se recomienda programar la siguiente instrucción con el programador de consultas de redshift. Se debe tener en cuenta que se debe correr antes de que se cumpla la retención de los datos en kinesis para evitar perdida de datos.

```sql
REFRESH MATERIALIZED VIEW v_streamlab;
```

Podemos visualizar la cantidad de registros que han llegado a Redshift

```sql
select 
    min(convert_timezone('America/Bogota',approximatearrivaltimestamp)),
    max(convert_timezone('America/Bogota',approximatearrivaltimestamp)),
    count(1)
from v_streamlab;
```

Los datos de los Sensores se pueden consultar a través del campo payload de tipo SUPER, se puede recurrir a PartiQL para acceder a los datos del campo.

```sql
select 
    payload
from v_streamlab;
```


## Referencias

- [Redshift Streaming Ingestion](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-streaming-ingestion.html) - ★(Preview)