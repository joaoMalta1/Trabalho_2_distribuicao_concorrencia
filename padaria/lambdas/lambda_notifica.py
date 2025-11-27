import json
import boto3
import os

sns_client = boto3.client('sns')

def lambda_handler(event, context):
    """
    Lambda 2: Recebe a mensagem pronta e dispara no SNS (email).
    """
    try:
        topic_arn = os.environ.get('TOPIC_ARN')
        mensagem = event.get("mensagem")

        if not mensagem:
            return {
                "statusCode": 400,
                "body": json.dumps({"erro": "Campo 'mensagem' não recebido"})
            }

        subject = "Atualização de Produto"

        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=mensagem,
            Subject=subject
        )

        print(f"Email enviado via SNS. ID: {response['MessageId']}")

        return {
            "status": "sucesso",
            "sns_message_id": response["MessageId"],
            "mensagem_enviada": mensagem
        }

    except Exception as e:
        print(f"Erro ao enviar SNS: {e}")
        return {
            "status": "erro",
            "erro": str(e)
        }
