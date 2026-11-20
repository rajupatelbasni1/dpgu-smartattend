from django.contrib import admin

from .models import *

admin.site.register(Category)
admin.site.register(EducationLevel)
admin.site.register(Post)
admin.site.register(PostSection)
admin.site.register(PostTable)
admin.site.register(PostTableRow)
admin.site.register(PostTableCell)

admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(QRHistory)
admin.site.register(Attendance)
