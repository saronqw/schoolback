from . import views
from django.urls import include, path
from rest_framework import routers

from .views import ListUsers, CoursesByDisciplineForTeacher, DisciplinesByCourseForTeacher, DisciplinesByTeacher, \
    ShowGrades, GradesForTeacher, GradesForStudent, GetChildren, GetCourses, GetTimetable

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'news', views.NewsViewSet)
router.register(r'newsimages', views.NewsImageViewSet)

router.register(r'courses', views.CourseViewSet)
router.register(r'disciplines', views.DisciplineViewSet)
router.register(r'educationplans', views.EducationPlanViewSet)
router.register(r'grades', views.GradeViewSet)
router.register(r'usershasclasses', views.UsersHasClassesViewSet)
router.register(r'timetables', views.TimetableViewSet)


# news_list = NewsViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
#
# news_detail = NewsViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
#
# news_image_list = NewsImageViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
#
# news_image_detail = NewsImageViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })

urlpatterns = [
    path('', include(router.urls)),
    # path('', news_list, name='news-list'),
    # path('<int:pk>/', news_detail, name='news-detail'),

    # path('', news_image_list, name='news-image-list'),
    # path('', news_image_detail, name='news-image-detail'),

    path('profile/<username>/', ListUsers.as_view(), name='user_profile'),
    path('courses_by_discipline/', CoursesByDisciplineForTeacher.as_view(), name='courses_by_discipline'),
    path('disciplines_by_course/', DisciplinesByCourseForTeacher.as_view(), name='disciplines_by_course'),
    path('disciplines_by_teacher/', DisciplinesByTeacher.as_view(), name='disciplines_by_teacher'),
    path('show_grades/', ShowGrades.as_view(), name='show_grades'),
    path('update_grade/', GradesForTeacher.as_view(), name='update_grade'),
    path('diary_grades/', GradesForStudent.as_view(), name='diary_grades'),
    path('get_children/', GetChildren.as_view(), name='get_children'),
    path('get_courses/', GetCourses.as_view(), name='get_courses'),
    path('get_timetable/', GetTimetable.as_view(), name='get_timetable'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
