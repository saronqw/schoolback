from django.contrib.auth.models import User
from django.db.models import *
from django.conf import settings


class NewsItem(Model):
    title = CharField(max_length=200)
    text = TextField()
    created = DateTimeField(auto_now_add=True)
    thumbnail = ImageField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "newsitem"


class NewsImage(Model):
    news_items = ManyToManyField(NewsItem, related_name='images')
    photo = ImageField(null=True)

    def __str__(self):
        return self.photo.name

    class Meta:
        db_table = "newsimage"


class Course(Model):
    level = IntegerField(null=False)
    level_letter = CharField(max_length=1)

    def __str__(self):
        return str(self.level) + self.level_letter

    class Meta:
        db_table = "course"


class Discipline(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "discipline"


class EducationPlan(Model):
    start_date = DateField()
    end_date = DateField(null=True)
    discipline = ForeignKey(Discipline, on_delete=CASCADE)
    course = ForeignKey(Course, on_delete=CASCADE)

    def __str__(self):
        return "Учебный год " + str(self.start_date) + "/" + str(self.end_date) + " " + \
               str(self.course.level) + self.course.level_letter + " " + self.discipline.name

    class Meta:
        db_table = "education_plan"


class Grade(Model):
    score = IntegerField()
    date_grading = DateField()
    education = ForeignKey(EducationPlan, on_delete=CASCADE)
    username = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    class Meta:
        db_table = "grade"


class UsersHasClasses(Model):
    admission_year = DateField()
    username = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    course = ForeignKey(Course, on_delete=CASCADE)

    def __str__(self):
        return "Год поступления " + str(self.admission_year) + " " + str(self.course.level) \
               + str(self.course.level_letter) + " " \
               + str((User.objects.get(username=self.username)).username)

    class Meta:
        db_table = "student_course"


class TeacherDiscipline(Model):
    username = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    education_plan = ForeignKey(EducationPlan, on_delete=CASCADE)

    class Meta:
        db_table = "teacher_discipline"


class Timetable(Model):
    date_discipline = DateTimeField()
    education_plan = ForeignKey(EducationPlan, on_delete=CASCADE)

    class Meta:
        db_table = "timetable"


class Parent(Model):
    parent = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    child = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="child")

    class Meta:
        db_table = "parent"

