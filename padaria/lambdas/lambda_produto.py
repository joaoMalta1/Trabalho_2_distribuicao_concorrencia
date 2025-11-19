import json
import boto3

lambda_client = boto3.client('lambda')
def lambda_handler(event, context):
    """
    Lambda 1: recebe tipo de alteração e aciona função lambda que comunica com sns 
    """
    try:
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)

        alteracao = (body["tipo_alteracao"])
        distribuidor = body["distribuidor"]
        produto_alterado = body["produto_nome"]

        payload = {
        "tipo_alteracao": alteracao,
        "distribuidor": distribuidor,
        "produto_nome": produto_alterado
        }

        response = lambda_client.invoke(
        FunctionName="Notifica",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload)
        )
        result = json.loads(response["Payload"].read())
        return result
    except Exception as e:
        return {
        "statusCode": 400,
        "body": json.dumps({"error": str(e)})
        }
