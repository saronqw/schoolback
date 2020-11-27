from news.models import *
from django.contrib.auth.models import User, Group
from rest_framework import serializers


class NewsImageOnlyUrl(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['photo']


class NewsImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsImage
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    images = NewsImageOnlyUrl(many=True)

    class Meta:
        model = NewsItem
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = '__all__'


class DisciplineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Discipline
        fields = '__all__'


class EducationPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = EducationPlan
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grade
        fields = '__all__'


class UsersHasClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersHasClasses
        fields = '__all__'


class TeacherDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherDiscipline
        fields = '__all__'


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'


class ParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parent
        fields = '__all__'
