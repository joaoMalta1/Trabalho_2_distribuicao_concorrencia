import base64
import json

def lambda_handler(event, context):
    try:
        headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()} #converte chavs para minusculas pra evitar erro 
        content_type = headers.get("content-type", "")

        if "multipart/form-data" not in content_type:
            return {
                "statusCode": 400,
                "body": json.dumps({"erro": "Content-Type inválido"})
            }

        body = event["body"]
        if event.get("isBase64Encoded"): #aws as vezes ja pega como base64
            body = base64.b64decode(body)

        boundary = content_type.split("boundary=")[1]
        boundary_bytes = boundary.encode()
        parts = body.split(boundary_bytes) #separa as partes do multipart form-data

        for part in parts:
            if b"Content-Disposition" in part and b"filename=" in part: #procura a parte que tem o arquivo
                file_data = part.split(b"\r\n\r\n", 1)[1] #pega o conteudo do arquivo
                file_data = file_data.rsplit(b"\r\n", 1)[0] #remove o \r\n do final

                img_base64 = base64.b64encode(file_data).decode("utf-8") #converte para base64

                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"base64": img_base64})
                }

        return {
            "statusCode": 400,
            "body": json.dumps({"erro": "Imagem não encontrada"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"erro": str(e)})
        }
