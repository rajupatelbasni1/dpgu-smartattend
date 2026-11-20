# from django.db import models

# class Category(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# class Education(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# class Job(models.Model):

#     TYPE_CHOICES = [
#         ("govt", "Government"),
#         ("private", "Private"),
#         ("upcoming", "Upcoming"),
#         ("result", "Result"),
#         ("admit", "Admit Card"),
#         ("answer", "Answer Key"),
#     ]

#     title = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)

#     job_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

#     department = models.CharField(max_length=255, blank=True, null=True)

#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
#     education = models.ManyToManyField(Education, blank=True)

#     total_posts = models.IntegerField(blank=True, null=True)
#     location = models.CharField(max_length=255, blank=True, null=True)

#     last_date = models.DateField(blank=True, null=True)
#     published_date = models.DateTimeField(auto_now_add=True)

#     short_desc = models.TextField(blank=True, null=True)
#     full_desc = models.TextField(blank=True, null=True)

#     notification_pdf = models.URLField(blank=True, null=True)
#     apply_link = models.URLField(blank=True, null=True)

#     is_featured = models.BooleanField(default=False)

#     class Meta:
#         ordering = ["-published_date"]

#     def __str__(self):
#         return self.title

## purana Db
from django.db import models
from django.utils import timezone


# class Category(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# class Education(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# class Job(models.Model):

#     TYPE_CHOICES = [
#         ("govt", "Government"),
#         ("private", "Private"),
#         ("upcoming", "Upcoming"),
#         ("result", "Result"),
#         ("admit", "Admit Card"),
#         ("answer", "Answer Key"),
#     ]

#     title = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)

#     job_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
#     department = models.CharField(max_length=255, blank=True, null=True)

#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
#     education = models.ManyToManyField(Education, blank=True)

#     location = models.CharField(max_length=255, blank=True, null=True)
#     age_limit = models.CharField(max_length=100, blank=True, null=True)

#     total_posts = models.IntegerField(blank=True, null=True)

#     apply_link = models.URLField(blank=True, null=True)
#     # notification_pdf = models.URLField(blank=True, null=True)
#     notification_pdf = models.FileField(
#         upload_to="notifications/",
#         null=True,
#         blank=True
#     )
#     short_desc = models.TextField(blank=True, null=True)
#     full_desc = models.TextField(blank=True, null=True)

#     # ⭐ SEO + Status fields
#     last_date = models.DateField(blank=True, null=True)

#     created_at = models.DateTimeField(auto_now_add=True)   # posted date
#     updated_at = models.DateTimeField(auto_now=True)       # updated date

#     def is_closed(self):
#         if self.last_date:
#             return self.last_date < timezone.now().date()
#         return False

#     def __str__(self):
#         return self.title

from django.db import models
from django.utils.text import slugify


# ===============================
# CATEGORY
# ===============================
class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ===============================
# EDUCATION
# ===============================
class EducationLevel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ===============================
# MAIN POST TABLE
# ===============================
class Post(models.Model):

    POST_TYPES = (
        ("job", "Job"),
        ("result", "Result"),
        ("admit", "Admit Card"),
        ("answer", "Answer Key"),
        ("syllabus", "Syllabus"),
        ("vacancy", "Vacancy"),
    )

    STATUS_TYPES = (
        ("open", "Open"),
        ("closed", "Closed"),
        ("upcoming", "Upcoming"),
    )

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)

    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_TYPES, default="open")

    department = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    education = models.ManyToManyField(EducationLevel, blank=True)

    total_posts = models.CharField(max_length=100, blank=True, null=True)
    age_limit = models.CharField(max_length=150, blank=True, null=True)
    salary = models.CharField(max_length=150, blank=True, null=True)

    apply_link = models.URLField(blank=True, null=True)
    notification_pdf = models.FileField(upload_to="notifications/", blank=True, null=True)

    last_date = models.DateField(blank=True, null=True)
    result_date = models.DateField(blank=True, null=True)
    admit_card_date = models.DateField(blank=True, null=True)
    exam_date = models.DateField(blank=True, null=True)

    short_desc = models.TextField(blank=True, null=True)
    full_desc = models.TextField(blank=True, null=True)

    seo_title = models.CharField(max_length=300, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ===============================
# SECTION (Important Dates etc)
# ===============================
class PostSection(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=200)
    position = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.post.title} - {self.title}"


# ===============================
# TABLE INSIDE SECTION
# ===============================
class PostTable(models.Model):
    section = models.ForeignKey(PostSection, on_delete=models.CASCADE, related_name="tables")
    title = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Table for {self.section.title}"


# ===============================
# ROW
# ===============================
class PostTableRow(models.Model):
    table = models.ForeignKey(PostTable, on_delete=models.CASCADE, related_name="rows")


# ===============================
# CELL
# ===============================
class PostTableCell(models.Model):
    row = models.ForeignKey(PostTableRow, on_delete=models.CASCADE, related_name="cells")
    column_index = models.IntegerField()
    value = models.TextField()

class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ("MCA", "MCA"),
        ("BCA", "BCA"),
        ("BBA", "BBA"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)

    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES
    )

    semester = models.CharField(max_length=20, blank=True)
    section = models.CharField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Faculty(models.Model):

    name = models.CharField(max_length=200)

    email = models.EmailField(unique=True)

    mobile = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

import uuid

# class QRHistory(models.Model):

#     token = models.UUIDField(default=uuid.uuid4, editable=False)

#     qr_image = models.ImageField(
#         upload_to="attendance_qr/",
#         blank=True,
#         null=True
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ("active","Active"),
#             ("inactive","Inactive")
#         ],
#         default="active"
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     expired_at = models.DateTimeField(blank=True,null=True)

#     generated_by = models.ForeignKey(
#         Faculty,
#         on_delete=models.SET_NULL,
#         null=True
#     )

#     def __str__(self):
#         return str(self.token)

class QRHistory(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False) #[cite: 4]
    qr_image = models.ImageField(upload_to="attendance_qr/", blank=True, null=True) #[cite: 4]
    status = models.CharField(max_length=20, choices=[("active","Active"), ("inactive","Inactive")], default="active") #[cite: 4]
    created_at = models.DateTimeField(auto_now_add=True) #[cite: 4]
    expired_at = models.DateTimeField(blank=True,null=True) #[cite: 4]
    generated_by = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True) #[cite: 4]

    # --- NAYE FIELDS ADD KAREIN ---
    is_location_restricted = models.BooleanField(default=False)  # Faculty on/off kar sake
    latitude = models.FloatField(null=True, blank=True)          # Faculty ki location
    longitude = models.FloatField(null=True, blank=True)         # Faculty ki location

    def __str__(self):
        return str(self.token) #[cite: 4]

# class Attendance(models.Model):

#     student = models.ForeignKey(
#         Student,
#         on_delete=models.CASCADE
#     )

#     # qr = models.ForeignKey(
#     #     QRHistory,
#     #     on_delete=models.CASCADE
#     # )
#     qr = models.ForeignKey(QRHistory, on_delete=models.CASCADE, null=True, blank=True)
#     date = models.DateField(auto_now_add=True)

#     time = models.TimeField(auto_now_add=True)

#     status = models.CharField(
#         max_length=10,
#         default="Present"
#     )

#     class Meta:
#         unique_together = (
#             "student",
#             "date"
#         )

#     def __str__(self):
#         return f"{self.student.name} - {self.date}"

import datetime
from django.utils import timezone

class Attendance(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )
    qr = models.ForeignKey(QRHistory, on_delete=models.CASCADE, null=True, blank=True)
    
    # LAMBDA FUNCTION USE KAR RAHE HAIN TAAKI LIVE DATE FETCH HO HAR BAAR
    date = models.DateField(default=timezone.now)  # ya fir: default=lambda: timezone.now().date()
    time = models.TimeField(default=timezone.now)

    status = models.CharField(
        max_length=10,
        default="Present"
    )

    class Meta:
        unique_together = (
            "student",
            "date"
        )

    def __str__(self):
        return f"{self.student.name} - {self.date}"