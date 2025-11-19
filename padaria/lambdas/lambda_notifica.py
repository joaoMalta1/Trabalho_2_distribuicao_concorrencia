import json
import boto3
import os

sns_client = boto3.client('sns')

def lambda_handler(event, context):
    """
    Lambda 2: Recebe dados, formata a mensagem e publica no SNS.
    """
    topic_arn = os.environ.get('TOPIC_ARN')
    produto = event.get("produto_nome", "Produto Desconhecido")
    alteracao = event.get("tipo_alteracao", 0)
    distribuidor = event.get("distribuidor", "Distribuidor N/A")

    subject = f"Alerta de Alteração: {produto}"
    message_text = f"O produto {produto} sofreu uma alteração de quantidade/status ({alteracao}) pelo distribuidor {distribuidor}."

    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message_text,
            Subject=subject
        )
        
        print(f"Email enviado via SNS. ID: {response['MessageId']}")
        return {
            "status": "sucesso",
            "sns_message_id": response['MessageId'],
            "mensagem_enviada": message_text
        }

    except Exception as e:
        print(f"Erro ao enviar SNS: {e}")
        raise e