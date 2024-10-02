from django.urls import path
from .views import (
    CourseListView, CoursesAllListView, CourseDetailView,
    ModuleListByCourseView, AllModuleListByCourseView, ModuleDetailView,
    LessonListByModuleView, RegisterCourseView, StatsView, 
    LessonDetailView, StudentLessonStartView, StudentLessonFinishView,
    ChatListView, SendMessageView
)

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('all/', CoursesAllListView.as_view(), name='courses_all'),
    path('<int:id>/', CourseDetailView.as_view(), name='course_detail'),

    path('modules/', ModuleListByCourseView.as_view(), name='module_list_by_course'),
    path('modules-all/', AllModuleListByCourseView.as_view(), name='all_module_list_by_course'),
    path('modules/<int:id>/', ModuleDetailView.as_view(), name='module_detail'),

    path('modules/<int:module_id>/chats/', ChatListView.as_view(), name='chat-list'),
    path('modules/<int:module_id>/send-message/', SendMessageView.as_view(), name='send_message'),

    path('register/<int:course_id>/', RegisterCourseView.as_view(), name='register_course'),
    path('stats/', StatsView.as_view(), name='stats'),
    
    path('lessons/', LessonListByModuleView.as_view(), name='lesson_list_by_module'),
    path('lessons/<int:id>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/start/<int:lesson_id>/', StudentLessonStartView.as_view(), name='start_lesson'),
    path('lessons/finish/<int:lesson_id>/', StudentLessonFinishView.as_view(), name='finish_lesson'),
]
