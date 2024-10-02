from docxtpl import DocxTemplate
from datetime import datetime
from io import BytesIO
import subprocess
import os
import tempfile

def generate_contract(enrollment, user, course):
    contract_id = enrollment.id
    today = datetime.now()
    day = today.day
    month = today.strftime("%B")
    student_name = user.username
    price = course.price

    template_path = 'courses/templates/contract.docx'
    doc = DocxTemplate(template_path)
    
    context = {
        'contract_id': contract_id,
        'day': day,
        'month': month,
        'student_name': student_name,
        'course_price': price,
    }

    doc.render(context)

    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    return file_stream

def convert_docx_to_pdf(docx_stream):
    temp_dir = tempfile.gettempdir()
    temp_docx_path = os.path.join(temp_dir, 'temp_contract.docx')
    temp_pdf_path = os.path.join(temp_dir, 'temp_contract.pdf')
    
    with open(temp_docx_path, 'wb') as f:
        f.write(docx_stream.read())

    try:
        command = ['python', 'C:\\scripts\\unoconv\\unoconv', '-f', 'pdf', '-o', temp_pdf_path, temp_docx_path]
        subprocess.run(command, check=True)

        with open(temp_pdf_path, 'rb') as pdf_file:
            pdf_stream = BytesIO(pdf_file.read())
    
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error converting DOCX to PDF: {e}")
    
    finally:
        if os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

    return pdf_stream
