from .models import Course, StudentAnswer, TestAnswer, TestQuestion, TestEnrollment
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError
from django.db import transaction
from .utils import generate_certificate
from django.core.files.base import ContentFile
import os

class CertificateService:
    @staticmethod
    def create_certificate(test_enrollment):
        if test_enrollment.certificate_file:
            return test_enrollment.certificate_file.name

        template_path = 'tests/templates/Sertifikat na\'muna.pptx'
        if not os.path.exists(template_path):
            raise ValidationError("Certificate template not found.")

        pdf_stream = generate_certificate(test_enrollment.student.username, template_path)

        filename = f'certificate_{test_enrollment.id}.pdf'
        test_enrollment.certificate_file.save(filename, ContentFile(pdf_stream.getvalue()))
        test_enrollment.save()

        return filename


class TestSubmissionService:
    @staticmethod
    @transaction.atomic
    def submit_test(enrollment_id, student, answers_data):
        enrollment = TestSubmissionService._get_enrollment(enrollment_id, student)

        if enrollment.finished:
            raise ValidationError("Test has already been submitted.")

        correct_answers_count = TestSubmissionService._process_answers(student, answers_data)

        enrollment.correct_answers = correct_answers_count
        enrollment.finished = True
        enrollment.save()

        return enrollment

    @staticmethod
    def _get_enrollment(enrollment_id, student):
        return get_object_or_404(TestEnrollment.objects.select_for_update(), id=enrollment_id, student=student)

    @staticmethod
    def _process_answers(student, answers_data):
        question_ids = [answer_data.get('question') for answer_data in answers_data]

        correct_answers = TestAnswer.objects.filter(question_id__in=question_ids, correct_answer=True)
        correct_answers_dict = {answer.question_id: answer.id for answer in correct_answers}

        correct_answers_count = 0
        for answer_data in answers_data:
            question_id = answer_data.get('question')
            selected_option = answer_data.get('option')

            if correct_answers_dict.get(question_id) == selected_option:
                correct_answers_count += 1

            TestSubmissionService._save_student_answer(student, question_id, selected_option)

        return correct_answers_count

    @staticmethod
    def _save_student_answer(student, question_id, selected_option):
        if StudentAnswer.objects.filter(student=student, question_id=question_id).exists():
            raise ValidationError(f"Answer for question {question_id} already submitted.")
        try:
            StudentAnswer.objects.create(
                answer_id=selected_option,
                question_id=question_id,
                student=student
            )
        except Exception as e:
            raise ValidationError(f"Error saving student answer: {str(e)}")


class TestGenerationService:
    @staticmethod
    def generate_test(user, course_id, test_type):
        course = get_object_or_404(Course, id=course_id)

        if test_type not in [1, 2]:
            raise ValidationError("Invalid test type.")

        existing_enrollment = TestGenerationService._get_existing_enrollment(user, course, test_type)
        
        if existing_enrollment:
            return existing_enrollment.id

        return TestGenerationService._create_test_enrollment(user, course, test_type)

    @staticmethod
    def _get_existing_enrollment(user, course, test_type):
        return TestEnrollment.objects.filter(
            student=user,
            course=course,
            type=test_type,
            finished=False
        ).first()

    @staticmethod
    @transaction.atomic
    def _create_test_enrollment(user, course, test_type):
        questions = TestQuestion.objects.filter(course=course, question_type=test_type)

        if not questions.exists():
            raise ValidationError("No questions available for this test type.")

        test_enrollment = TestEnrollment.objects.create(
            student=user,
            course=course,
            type=test_type,
            total_questions=questions.count(),
            correct_answers=0,
            finished=False
        )

        test_enrollment.questions.set(questions)
        test_enrollment.save()

        return test_enrollment.id
