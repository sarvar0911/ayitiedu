import subprocess
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Course, Enrollment, Lesson, Module, StudentLessonProgress, ChatMessage
from .utils import generate_contract, convert_docx_to_pdf
from django.core.files.base import ContentFile


class ContractService:
    @staticmethod
    @transaction.atomic
    def create_contract(enrollment, user, course):
        if enrollment.contract_file:
            return enrollment.contract_file.name
        
        try:
            contract_file_stream = generate_contract(enrollment, user, course)
            pdf_file_stream = convert_docx_to_pdf(contract_file_stream)
            contract_filename = f'contract_{enrollment.id}.pdf'
            enrollment.contract_file.save(contract_filename, ContentFile(pdf_file_stream.read()))
            enrollment.save()
            return contract_filename
        
        except subprocess.CalledProcessError as e:
            print(f"Error converting DOCX to PDF: {str(e)}")
            raise ValidationError("Failed to generate contract PDF.")
        
        except FileNotFoundError as e:
            print(f"Template file not found: {str(e)}")
            raise ValidationError("Contract template is missing.")
        
        except Exception as e:
            print(f"Error generating contract: {str(e)}")
            raise ValidationError("An error occurred while generating the contract.")


class EnrollmentService:
    @staticmethod
    @transaction.atomic
    def register_user_for_course(user, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        enrollment = Enrollment.objects.filter(user=user, course=course).first()
        
        if enrollment:
            return enrollment, None, "User already enrolled"
        
        enrollment = Enrollment.objects.create(user=user, course=course)
        contract_filename = ContractService.create_contract(enrollment, user, course)
        return enrollment, contract_filename, "User successfully enrolled"


class StudentLessonProgressService:
    @staticmethod
    @transaction.atomic
    def start_lesson(student, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        progress, created = StudentLessonProgress.objects.get_or_create(student=student, lesson=lesson)
        
        if progress.started_date:
            return None 
        
        progress.started_date = timezone.now()
        progress.save()
        return progress

    @staticmethod
    @transaction.atomic
    def finish_lesson(student, lesson_id):
        progress = StudentLessonProgress.objects.select_for_update().get(student=student, lesson_id=lesson_id)
        
        if progress.completed_date:
            return None 
        
        progress.completed_date = timezone.now()
        progress.save()
        return progress


class StatsService:
    @staticmethod
    def get_statistics():
        from django.contrib.auth import get_user_model
        User = get_user_model()
        courses_count = Course.objects.count()
        teachers_count = User.objects.filter(role='teacher').count() or 0
        students_count = User.objects.filter(role='student').count() or 0

        return {
            'courses_count': courses_count,
            'teachers_count': teachers_count,
            'students_count': students_count,
        }


class ChatService:
    @staticmethod
    def send_message(user, data):
        module = get_object_or_404(Module, id=data.get('module'))
        
        reply_message = None
        if reply_id := data.get('reply'):
            reply_message = get_object_or_404(ChatMessage, id=reply_id)

        return ChatMessage.objects.create(
            module=module,
            user=user,
            message=data['message'],
            type=data.get('type', 1),
            reply=reply_message
        )
