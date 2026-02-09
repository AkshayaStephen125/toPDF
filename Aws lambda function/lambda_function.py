import json
import fpdf
import boto3
import base64
from fpdf import FPDF
from io import BytesIO
import uuid
from PIL import Image
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

s3 = boto3.client("s3")

BUCKET_NAME = "pdfy-it"

def lambda_handler(event, context):
    # TODO implement

    file_type = event['file_type']
    file_content = event['file_content']
    print(file_type)

    match file_type:
        case "text":
            result, message, file_name = convert_txt_to_pdf(file_content)
        case "image":
            result, message, file_name = convert_image_to_pdf(file_content)
        case "doc":
            result, message, file_name = convert_doc_to_pdf(file_content)
        case _:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "error": "Invalid file type"
                })
            }
    if result:
        return {
                'statusCode': 200,
                'body': json.dumps({
                    "message": "PDF generated and stored in S3",
                    "s3_key": file_name
                })
            }
    else:
        return {
                'statusCode': 500,
                'body': json.dumps({
                    "error": message
                })
            }

    
def convert_txt_to_pdf(text):
    result = False
    message = ''
    file_name = ''
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in text.split("\n"):
            pdf.multi_cell(0, 8, line)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        file_name = f"text/{uuid.uuid4()}.pdf"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=pdf_bytes,
            ContentType="application/pdf"
        )
        result = True
        message = "PDF generated and stored in S3"
    except Exception as e:
        message = str(e)
        print(message)
        return result, message, file_name

    return result, message, file_name

def convert_image_to_pdf(image_base64):
    result = False
    message = ''
    file_name = ''
    try:
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        pdf_buffer = BytesIO()
        image.save(pdf_buffer, format="PDF")
        pdf_buffer.seek(0)

        file_name = f"images/{uuid.uuid4()}.pdf"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=pdf_buffer.getvalue(),
            ContentType="application/pdf"
        )

        result = True
        message = "PDF generated and stored in S3"
    except Exception as e:
        message = str(e)
        print(message)
        return result, message, file_name

    return result, message, file_name


def convert_doc_to_pdf(file_base64):
    result = False
    message = ''
    file_name = ''
    try:
        file_bytes = base64.b64decode(file_base64)

        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4
        y = height - 40
        doc = Document(BytesIO(file_bytes))
        for para in doc.paragraphs:
            pdf.drawString(40, y, para.text)
            y -= 15
            if y < 40:
                pdf.showPage()
                y = height - 40
        pdf.save()
        pdf_buffer.seek(0)
        file_name = f"docs/{uuid.uuid4()}.pdf"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=pdf_buffer.getvalue(),
            ContentType="application/pdf"
        )

        result = True
        message = "PDF generated and stored in S3"
    except Exception as e:
        message = str(e)
        print(message)
        return result, message, file_name

    return result, message, file_name