from user_app.models import UploadedFile
from fpdf import FPDF
from io import BytesIO
import base64
import boto3
import json

def convert_to_pdf(file_type, uploaded_file):
    download_url = ''
    message = ''
    try:
        match file_type:
            case "text":
                result, message, download_url = convert_text_to_pdf(file_type, uploaded_file)
            case "image":
                result, message, download_url = convert_image_to_pdf(file_type, uploaded_file)
            case "doc":
                result, message, download_url = convert_doc_to_pdf(file_type, uploaded_file)
            case _:
                return False, "Invalid file type"
        if result:
            return True, "Your PDF is ready", download_url
        else:
            return False, message, download_url
    except Exception as e:
        print(e)
        return False, str(e)
        
def convert_text_to_pdf(file_type, text):
    result = False
    message = ''
    try:
        payload = {"file_type" : file_type, 
                "file_content": text}
        response = invoke_lambda_function(payload)
        if response:
            download_url = generate_download_url(response)
            result = True
    except Exception as e:
        message = str(e)
    return result, message, download_url

def convert_image_to_pdf(file_type, uploaded_file):
    result = False
    message = ''
    download_url = ''
    try:
        allowed_extensions = (".jpg", ".jpeg", ".png")
        allowed_mime_types = ("image/jpeg", "image/png")

        filename = uploaded_file.name.lower()
        content_type = uploaded_file.content_type

        if not filename.endswith(allowed_extensions):
            return False, "Only JPG and PNG images are allowed"

        if content_type not in allowed_mime_types:
            return False, "Invalid image file type"
        
        encoded_image = base64.b64encode(uploaded_file.read()).decode("utf-8")

        payload = {"file_type" : file_type, 
                "file_content": encoded_image}
        
        response = invoke_lambda_function(payload)

        if response:
            download_url = generate_download_url(response)
            result = True
    except Exception as e:
        message = str(e)
    return result, message, download_url

def convert_doc_to_pdf(file_type, uploaded_file):
    result = False
    message = ''
    download_url = ''
    try:
        allowed_extensions = (".doc", ".docx")
        allowed_mime_types = (
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        filename = uploaded_file.name.lower()
        content_type = uploaded_file.content_type

        if not filename.endswith(allowed_extensions):
            return False, "Only DOC and DOCX files are allowed"

        if content_type not in allowed_mime_types:
            return False, "Invalid document file type"


        encoded_doc = base64.b64encode(uploaded_file.read()).decode("utf-8")

        if not encoded_doc:
            return False, "Uploaded document is empty"
        
        payload = {"file_type" : file_type, 
                "file_content": encoded_doc}
        response = invoke_lambda_function(payload)
        if response:
            download_url = generate_download_url(response)
            result = True
    except Exception as e:
        message = str(e)
    return result, message, download_url

def invoke_lambda_function(payload):
    try:
        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName='generate-pdf',
            Payload=json.dumps(payload)
        )
        return response
    except Exception as e:
        print(f"Error invoking Lambda function: {str(e)}")
        return None
    
def generate_download_url(response):
    payload = json.loads(response["Payload"].read())
    body = json.loads(payload["body"])

    s3_key = body["s3_key"]
    s3 = boto3.client("s3")
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": 'pdfy-it', "Key": s3_key},
        ExpiresIn=300 
    )

