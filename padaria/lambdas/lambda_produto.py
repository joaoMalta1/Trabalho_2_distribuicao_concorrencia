import json
import boto3

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    Lambda 1: Recebe a alteração e aciona a Lambda Notifica com a mensagem correta
    """
    try:
        body = event.get("body")

        if isinstance(body, str):
            body = json.loads(body)

        alteracao = body["tipo_alteracao"]
        distribuidor = body["distribuidor"]
        produto_alterado = body["produto_nome"]

        if alteracao == "disponivel":
            mensagem = (
                f"O produto '{produto_alterado}' do distribuidor '{distribuidor}' "
                f"já está disponível! Você já pode ir até a loja para realizar a compra."
            )
        else:
            mensagem = (
                f"O distribuidor '{distribuidor}' ainda não possui o produto "
                f"'{produto_alterado}' sem estoque. Assim que estiver disponível você será avisado."
            )

        payload = {
            "mensagem": mensagem
        }

        response = lambda_client.invoke(
            FunctionName="Notifica",
            InvocationType="RequestResponse",
            Payload=json.dumps(payload)
        )

        result = json.loads(response["Payload"].read())

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "Mensagem enviada com sucesso",
                "mensagem_enviada": mensagem,
                "retorno_notifica": result
            })
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
