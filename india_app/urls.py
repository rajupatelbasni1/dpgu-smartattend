# from django.urls import path
# from .attendance_views import *

# # from .views import jobs_list , add_job , job_detail
# from .views import latest_posts, post_list, post_detail , search_jobs ,posts_by_category
# from india_app import attendance_views

# urlpatterns = [

#     # path("jobs/", jobs_list),   # 👈 new API
#     # path("add-job/", add_job),
#     # path("jobs/<slug:slug>/", job_detail),
    
#     path("posts/latest/", latest_posts),
#     path("posts/", post_list),
#     path("posts/<slug:slug>/", post_detail),
#     path("search/", search_jobs),
#     path("posts/category/<slug:category_slug>/", posts_by_category),
#     path("attendance/login/", student_login),

#  path("attendance/login/", student_login),
# path("attendance/faculty-login/", faculty_login),
# path("attendance/dashboard/", dashboard),
# path("attendance/generate-qr/", generate_qr),
# path("attendance/qr-history/", qr_history),
# path("attendance/scan/", scan_qr),
# # path("attendance/export/", export_csv),
# path("attendance/students/", student_list),
# path("attendance/add-student/", add_student),
# path("attendance/delete-student/<int:id>/", delete_student),

#     path("attendance/generate-qr/", generate_qr),
# path("attendance/active-qr/", active_qr),
# path("attendance/qr-history/", qr_history),
# path("attendance/qr/<int:id>/", qr_detail),
# path("attendance/deactivate-qr/<int:id>/", deactivate_qr),
# path("attendance/delete-qr/<int:id>/", delete_qr),

# path("attendance/scan/", scan_qr),

# path("attendance/history/", attendance_history),

# path("attendance/export/all/", export_all_csv),

# path("attendance/export/present/", export_present_csv),

# path("attendance/export/absent/", export_absent_csv),

# path("attendance/export/summary/", export_summary_csv),
# path("attendance/deactivate-qr/<int:id>/", deactivate_qr),
# path("attendance/activate-qr/<int:id>/", activate_qr),  # Ye line add karein
# path("attendance/delete-qr/<int:id>/", delete_qr),
# # Baki attendance URLs ke neeche ye add karein
# path("attendance/atlas-a-students/", get_atlas_a_students),
# path("attendance/atlas-b-students/", get_atlas_b_students),
# path("attendance/sync-mongo/", sync_mongo_data),
# path("attendance/faculty/", get_faculties),
# # Reports & Actions URLs
#     path("attendance/report-view/", report_view),
#     path("attendance/mark-all-absent/", mark_all_absent),
    
#     # Advanced CSV Export URLs
#     path("attendance/export/daily/", export_daily),
#     path("attendance/export/weekly/", export_weekly),
#     path("attendance/export/monthly/", export_monthly),
#     path("attendance/export/all/", export_all),

# #    path('sync-atlas-a-to-b/', attendance_views.sync_atlas_a_to_b, name='sync_atlas_a_to_b'),
# #     path('get-dpgu-students/', attendance_views.get_dpgu_students, name='get_dpgu_students'),
    
# #     # Dhyan rahe, generate-qr wala bhi naya function humne banaya tha views me
# #     path('generate-qr/', attendance_views.generate_qr_code, name='generate_qr_code'),
# #     path('get-dpgu-faculties/', attendance_views.get_dpgu_faculties, name='get_dpgu_faculties'),


#     path('generate-qr/', attendance_views.generate_qr_code, name='generate_qr_code'),

#     path('attendance/get-dpgu-faculties/', attendance_views.get_dpgu_faculties, name='get_dpgu_faculties'),
#     path('attendance/get-atlas-a-students/', attendance_views.get_atlas_a_students, name='get_atlas_a_students'),
#     path('attendance/get-dpgu-students/', attendance_views.get_dpgu_students, name='get_dpgu_students'),
#     path('attendance/sync-atlas-a-to-b/', attendance_views.sync_atlas_a_to_b, name='sync_atlas_a_to_b'),
# ]


from django.urls import path
from .views import latest_posts, post_list, post_detail , search_jobs ,posts_by_category
from india_app import attendance_views

urlpatterns = [
    # Blog / Jobs URLs
    path("posts/latest/", latest_posts),
    path("posts/", post_list),
    path("posts/<slug:slug>/", post_detail),
    path("search/", search_jobs),
    path("posts/category/<slug:category_slug>/", posts_by_category),

    # ==========================================
    # 🚫 PURANE SQLITE URLS (SKIPPED / HIDDEN)
    # ==========================================
    # path("attendance/dashboard/", dashboard),
    # path("attendance/generate-qr/", generate_qr),
    # path("attendance/qr-history/", qr_history),
    # path("attendance/report-view/", report_view),
    # path("attendance/mark-all-absent/", mark_all_absent),
    # path("attendance/deactivate-qr/<int:id>/", deactivate_qr),
    # path("attendance/activate-qr/<int:id>/", activate_qr),
    
    # ==========================================
    # ✅ NAYE MONGODB ATLAS B URLS (ACTIVE)
    # ==========================================
    
    # 1. Login & Sync Pipeline
    path('attendance/get-dpgu-faculties/', attendance_views.get_dpgu_faculties, name='get_dpgu_faculties'),
    path('attendance/get-atlas-a-students/', attendance_views.get_atlas_a_students, name='get_atlas_a_students'),
    path('attendance/get-dpgu-students/', attendance_views.get_dpgu_students, name='get_dpgu_students'),
    path('attendance/sync-atlas-a-to-b/', attendance_views.sync_atlas_a_to_b, name='sync_atlas_a_to_b'),
    # path('attendance/setup-faculty/', attendance_views.setup_faculty_collection, name='setup_faculty_collection'),

    # 2. Dashboard
    path('attendance/dashboard/', attendance_views.dashboard, name='dashboard'),

    # 3. QR Management (MongoDB ki ID string hoti hai, isliye <str:id> use kiya hai)
    path('attendance/generate-qr/', attendance_views.generate_qr_code, name='generate_qr_code'),
    path('attendance/qr-history/', attendance_views.qr_history, name='qr_history'),
    path('attendance/deactivate-qr/<str:id>/', attendance_views.deactivate_qr, name='deactivate_qr'),
    path('attendance/activate-qr/<str:id>/', attendance_views.activate_qr, name='activate_qr'),

    # 4. Reports & Bulk Action
    path('attendance/report-view/', attendance_views.report_view, name='report_view'),
    path('attendance/mark-all-absent/', attendance_views.mark_all_absent, name='mark_all_absent'),
    
    # ----------------------------------------------------
    # (Student App & Backup URLs - Untouched as requested)
    path("attendance/login/", attendance_views.student_login),
    path("attendance/scan/", attendance_views.scan_qr),
    path("attendance/history/", attendance_views.attendance_history),
    path("attendance/export/daily/", attendance_views.export_daily),
    path("attendance/export/weekly/", attendance_views.export_weekly),
    path("attendance/export/monthly/", attendance_views.export_monthly),
    path("attendance/export/all/", attendance_views.export_all),



    path('attendance/manual-present/', attendance_views.mark_manual_present, name='mark_manual_present'),
    path('attendance/send-absent-emails/', attendance_views.send_absent_emails, name='send_absent_emails'),

   
    path('attendance/check-face/', attendance_views.check_face_registration, name='check-face'),
    path('attendance/register-face/', attendance_views.register_face, name='register-face'),
    path('attendance/mark-face-attendance/', attendance_views.mark_face_attendance, name='mark-face-attendance'),
    # Faculty Face Settings URLs
    path('attendance/get-face-settings/', attendance_views.get_face_settings, name='get-face-settings'),
    path('attendance/update-face-settings/', attendance_views.update_face_settings, name='update-face-settings'),
]