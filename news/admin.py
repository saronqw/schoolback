# Register your models here.
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import NewsItem, NewsImage, Course, Discipline, EducationPlan, Grade, UsersHasClasses, TeacherDiscipline, \
    Timetable, Parent


class MembershipInline(admin.TabularInline):
    model = NewsImage.news_items.through
    extra = 1


class NewsItemAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    list_display = ('title', 'short_text', 'created')
    list_filter = ['created']

    def short_text(self, obj):
        word_list = (obj.text.split(" ")[:20])
        description = ""
        for word in word_list:
            description += word + " "
        return description.rstrip() + "..."

    short_text.short_description = 'Text'


class NewsImageAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    list_display = ('image_tag', 'photo')
    exclude = ('news_items',)

    def image_tag(self, obj):
        return mark_safe('<img src="%s" width="150" height="150" />' % obj.photo.url)

    image_tag.short_description = 'Image'


admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(NewsImage, NewsImageAdmin)
admin.site.register(Course)
admin.site.register(Discipline)
admin.site.register(EducationPlan)
admin.site.register(Grade)
admin.site.register(UsersHasClasses)
admin.site.register(TeacherDiscipline)
admin.site.register(Timetable)
admin.site.register(Parent)
