# Create your views here.
import datetime
import json

from django.contrib.auth.models import User, Group
from django.db import connection
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from news.models import NewsItem, NewsImage, Course, Discipline, EducationPlan, Grade, UsersHasClasses, \
    TeacherDiscipline, Timetable, Parent
from news.serializers import UserSerializer, GroupSerializer, NewsImageSerializer, NewsSerializer, CourseSerializer, \
    DisciplineSerializer, EducationPlanSerializer, GradeSerializer, UsersHasClassesSerializer, \
    TeacherDisciplineSerializer, ParentSerializer


class NewsResultsSetPagination(LimitOffsetPagination):
    page_size = 3


class NewsViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = NewsItem.objects.all()
    serializer_class = NewsSerializer
    pagination_class = NewsResultsSetPagination
    # permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]


class NewsImageViewSet(viewsets.ModelViewSet):
    queryset = NewsImage.objects.all()
    serializer_class = NewsImageSerializer
    # permission_classes = [permissions.IsAuthenticated]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class DisciplineViewSet(viewsets.ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer


class EducationPlanViewSet(viewsets.ModelViewSet):
    queryset = EducationPlan.objects.all()
    serializer_class = EducationPlanSerializer


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class UsersHasClassesViewSet(viewsets.ModelViewSet):
    queryset = UsersHasClasses.objects.all()
    serializer_class = UsersHasClassesSerializer


class TeacherDisciplineViewSet(viewsets.ModelViewSet):
    queryset = UsersHasClasses.objects.all()
    serializer_class = TeacherDiscipline


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = Timetable


class ListUsers(APIView):
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request, username):
        user = User.objects.get(username=username)
        group = list(user.groups.values_list('name', flat=True))[0]

        profile_json = {
            "username": user.username,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "group": group,
            # "course": course_data.data,
        }

        if group == "student":
            # search student course
            users_classes = UsersHasClasses.objects.filter(username_id=user.id)
            course_data = UsersHasClassesSerializer(users_classes, many=True)
            course_id = dict(course_data.data[0]).get("course")
            course = Course.objects.get(id=course_id)
            profile_json["course"] = str(course.level) + course.level_letter
            profile_json["admission_year"] = dict(course_data.data[0]).get("admission_year")[:4]

        return Response(profile_json)


class CoursesByDisciplineForTeacher(APIView):

    def get(self, request):
        teacher = request.user
        teacher_id = '"' + str(User.objects.get(username=teacher).id) + '"'
        discipline = '"' + request.query_params["discipline"] + '"'
        courses = Course.objects.raw("\
                          SELECT course.id, course.level, course.level_letter \
                          FROM teacher_discipline \
                          JOIN education_plan ON education_plan.id = teacher_discipline.education_plan_id \
                          JOIN discipline ON education_plan.discipline_id = discipline.id \
                          JOIN course ON course.id = education_plan.course_id \
                          JOIN auth_user ON teacher_discipline.username_id = auth_user.id \
                          WHERE auth_user.id = " + teacher_id + " and discipline.name = " + discipline)

        response_json = {
            "courses": []
        }

        for course in courses:
            response_json["courses"].append(dict(level=course.level, level_letter=course.level_letter))

            # response_json["courses"].append(dict('{ "level": ' + str(course.level) + ', '
            #                                     + '"level_letter": "' + course.level_letter + '"}'))
        # teacher_queryset = TeacherDiscipline.objects.all()
        # teacher_data = TeacherDisciplineSerializer(teacher_queryset, many=True)
        # print(teacher_data.data)
        # return Response(teacher_data.data)
        return Response(response_json)


class DisciplinesByCourseForTeacher(APIView):

    def get(self, request):
        teacher = request.user
        teacher_id = '"' + str(User.objects.get(username=teacher).id) + '"'
        course_level = str(request.query_params.get('course_level'))
        course_letter = '"' + request.query_params.get('course_level_letter') + '"'
        disciplines = Discipline.objects.raw(f"\
                          SELECT discipline.id, discipline.name \
                          FROM teacher_discipline \
                          JOIN education_plan ON education_plan.id = teacher_discipline.education_plan_id \
                          JOIN discipline ON education_plan.discipline_id = discipline.id \
                          JOIN course ON course.id = education_plan.course_id \
                          JOIN auth_user ON teacher_discipline.username_id = auth_user.id \
                          WHERE auth_user.id = {teacher_id} and course.level = {course_level} and course.level_letter = {course_letter}")

        response_json = {
            "disciplines": []
        }

        for discipline in disciplines:
            response_json["disciplines"].append(discipline.name)

        return Response(response_json)


class DisciplinesByTeacher(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        teacher = request.user
        teacher_id = User.objects.get(username=teacher).id
        disciplines = Discipline.objects.filter(educationplan__teacherdiscipline__username_id=teacher_id)
        disciplines_data = DisciplineSerializer(disciplines, many=True)
        return Response(disciplines_data.data)


class ShowGrades(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    # def dictfetchall(cursor):
    #     columns = [col[0] for col in cursor]
    #     return [
    #         dict(zip(columns, row))
    #         for row in cursor.fetchall()
    #     ]

    def get(self, request):
        course_level = request.query_params.get('course_level')
        course_level_letter = '"' + request.query_params.get('course_level_letter') + '"'
        discipline = '"' + request.query_params.get('discipline') + '"'
        date_now = request.query_params.get('date')

        sql_query = f'SELECT grade.id, DATE(timetable.date_discipline) as date, auth_user.last_name, auth_user.first_name, grade.score, auth_user.username \
                FROM timetable \
                JOIN education_plan ON timetable.education_plan_id = education_plan.id \
                AND DATE(timetable.date_discipline) LIKE "{date_now}-%%" \
                JOIN discipline ON education_plan.discipline_id = discipline.id AND discipline.name = {discipline} \
                JOIN course ON education_plan.course_id = course.id AND course.level = {course_level} AND course.level_letter = {course_level_letter}\
                JOIN student_course ON student_course.course_id = course.id \
                JOIN auth_user ON student_course.username_id = auth_user.id \
                LEFT JOIN grade ON grade.education_id = education_plan.id  \
                AND DATE(timetable.date_discipline) = grade.date_grading \
                AND grade.username_id = auth_user.id \
                ORDER BY auth_user.username'

        response_json = {
            "dates": [],
            "students": []
        }

        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            connection.commit()

            all_row = cursor.fetchall()

            for row in all_row:
                row_list = list(row)
                date = row_list[1]
                if date not in response_json["dates"]:
                    response_json["dates"].append(date)

            response_json["dates"].sort()

            prev_student = None
            student_object = dict()
            for row in all_row:
                row_list = list(row)
                date = row_list[1]
                last_name = row_list[2]
                first_name = row_list[3]
                grade = row_list[4]
                username = row_list[5]

                name = last_name + " " + first_name
                if prev_student != name:
                    if student_object:
                        response_json["students"].append(student_object)
                    student_object = dict()
                    prev_student = name
                    student_object["name"] = prev_student
                    student_object["username"] = username
                    student_object["grades"] = list()

                    if grade is not None:
                        student_object["grades"].append({"date": date, "grade": grade})

                elif prev_student == name:
                    if grade is not None:
                        student_object["grades"].append({"date": date, "grade": grade})
            if student_object:
                response_json["students"].append(student_object)
        return Response(response_json)


class GradesForTeacher(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        grade = request.query_params.get('grade')
        date_grading = '"' + str(
            datetime.datetime.strptime(request.query_params.get('date_grading')[:10], '%Y-%m-%d').date()) + '"'
        date_grading_without = str(
            datetime.datetime.strptime(request.query_params.get('date_grading')[:10], '%Y-%m-%d').date())
        discipline = '"' + request.query_params.get('discipline') + '"'
        user_id = User.objects.get(username=request.query_params.get('username')).id
        course_level = request.query_params.get('course_level')
        course_level_letter = '"' + request.query_params.get('course_level_letter') + '"'

        sql_query = f'SELECT grade.id, grade.score, education_plan.id AS education_id \
                FROM education_plan \
                JOIN discipline ON discipline.id = education_plan.discipline_id AND discipline.name = {discipline} \
                JOIN course ON education_plan.course_id = course.id AND course.level = {course_level} AND course.level_letter = {course_level_letter} \
                LEFT JOIN grade ON grade.education_id = education_plan.id AND grade.date_grading =  {date_grading} \
                LEFT JOIN auth_user ON auth_user.id = grade.username_id AND auth_user.id = {user_id}'

        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            connection.commit()
            row = cursor.fetchone()
            education_id = row[2]

            if row[0] is None:
                grade_insert = Grade(score=grade, date_grading=date_grading_without, education_id=education_id,
                                     username_id=user_id)
                grade_insert.save()
            elif grade == "":
                Grade(id=row[0]).delete()
            elif row[0] is not None:
                Grade.objects.filter(id=row[0]).update(score=grade)

        return Response()


class GradesForStudent(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        child_id = request.query_params.get('child_id')
        offset = request.query_params.get('offset')
        user = request.user
        user_id = User.objects.get(username=user).id

        if child_id is not None:
            user_id = child_id

        sql_query = f'\
            SELECT grade.id, dayname(timetable.date_discipline) AS day, DATE(timetable.date_discipline), discipline.name, grade.score \
            FROM discipline \
            JOIN education_plan ON discipline.id = education_plan.discipline_id \
            JOIN course ON course.id = education_plan.course_id \
            JOIN student_course ON course.id = student_course.course_id AND student_course.username_id = {user_id} \
            JOIN timetable ON timetable.education_plan_id = education_plan.id \
            AND DATE(timetable.date_discipline) >= FIRST_DAY_OF_WEEK(ADDDATE(NOW(), {offset})) \
            AND DATE(timetable.date_discipline) <= LAST_DAY_OF_WEEK(ADDDATE(NOW(), {offset})) \
            LEFT JOIN grade ON grade.education_id = education_plan.id \
            AND DATE(timetable.date_discipline) = grade.date_grading \
            AND  grade.username_id = student_course.username_id \
            ORDER BY timetable.date_discipline'

        response_json = {
            "diary": [
                # {
                #     "weekday": None,
                #     "date": None,
                #     "grades": [
                #       {
                #           "discipline": None,
                #           "grade": None
                #       }
                #     ]
                # }
            ]
        }

        with connection.cursor() as cursor:
            cursor.execute("SET lc_time_names = 'ru_RU'")
            cursor.execute(sql_query)
            connection.commit()
            all_row = cursor.fetchall()

        prev_day = "NoneDay"
        day_object = dict()
        for row in all_row:
            row_list = list(row)
            weekday = row_list[1]
            date_grading = row_list[2]
            discipline = row_list[3]
            grade = row_list[4]

            day_now = weekday
            if prev_day != day_now:
                if day_object:
                    response_json["diary"].append(day_object)
                day_object = dict()
                prev_day = day_now
                day_object["weekday"] = prev_day
                day_object["date"] = date_grading
                day_object["grades"] = list()

                # if grade is not None:
                day_object["grades"].append({"discipline": discipline, "grade": grade})

            elif prev_day == day_now:
                # if grade is not None:
                day_object["grades"].append({"discipline": discipline, "grade": grade})
        if day_object:
            response_json["diary"].append(day_object)

        return Response(response_json)


class GetChildren(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        parent = request.user
        parent_id = User.objects.get(username=parent).id
        children = Parent.objects.filter(parent_id=parent_id)
        children_data = ParentSerializer(children, many=True)

        children_array = []
        for children_object in json.loads(json.dumps(children_data.data)):
            children_array.append(children_object["child"])

        user_objects = User.objects.filter(id__in=children_array)
        print(user_objects)
        children_serializing = UserSerializer(user_objects, many=True)

        children_response = []
        for element in children_serializing.data:
            children_response.append(dict(id=element["id"], first_name=element["first_name"]))

        return Response(children_response)


class GetTimetable(APIView):

    def get(self, request):
        course_level = request.query_params.get('course_level')
        course_level_letter = '"' + request.query_params.get('course_level_letter') + '"'

        sql_query = f'\
                    SELECT dayname(timetable.date_discipline) AS weekday, \
                    TIME_FORMAT(TIME(timetable.date_discipline), "%H:%i") AS time, \
                    discipline.name \
                    FROM discipline \
                    JOIN education_plan ON discipline.id = education_plan.discipline_id \
                    JOIN course ON course.id = education_plan.course_id \
                    AND course.level = {course_level} \
                    AND course.level_letter = {course_level_letter} \
                    JOIN timetable ON timetable.education_plan_id = education_plan.id \
                    AND DATE(timetable.date_discipline) >= FIRST_DAY_OF_WEEK(NOW()) \
                    AND DATE(timetable.date_discipline) <= LAST_DAY_OF_WEEK(NOW()) \
                    ORDER BY timetable.date_discipline'

        response_json = []

        with connection.cursor() as cursor:
            cursor.execute("SET lc_time_names = 'ru_RU'")
            cursor.execute(sql_query)
            connection.commit()
            all_row = cursor.fetchall()

        prev_day = "NoneDay"
        day_object = dict()
        for row in all_row:
            row_list = list(row)
            weekday = row_list[0]
            time = row_list[1]
            discipline = row_list[2]

            day_now = weekday
            if prev_day != day_now:
                if day_object:
                    response_json.append(day_object)
                day_object = dict()
                prev_day = day_now
                day_object["weekday"] = prev_day
                day_object["disciplines"] = list()
                day_object["disciplines"].append({"time": time, "discipline": discipline})

            elif prev_day == day_now:
                day_object["disciplines"].append({"time": time, "discipline": discipline})

        response_json.append(day_object)

        return Response(response_json)


class GetCourses(APIView):

    def get(self, request):
        courses_objects = Course.objects.order_by('level', 'level_letter')
        courses_serializing = CourseSerializer(courses_objects, many=True)

        return Response(courses_serializing.data)
