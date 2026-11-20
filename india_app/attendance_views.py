from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Faculty, QRHistory

from .models import *

import csv
import uuid
import qrcode
import os
import json
import datetime
from django.conf import settings


# =====================================================
# STUDENT LOGIN
# =====================================================

@api_view(["POST"])
def student_login(request):

    email = request.data.get("email")
    mobile = request.data.get("mobile")

    try:

        student = Student.objects.get(
            email=email,
            mobile=mobile
        )

        return Response({
            "success": True,
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "department": student.department,
            "semester": student.semester,
            "section": student.section
        })

    except Student.DoesNotExist:

        return Response({
            "success": False,
            "message": "Invalid Email or Mobile"
        })


# =====================================================
# FACULTY LOGIN
# =====================================================

@api_view(["POST"])
def faculty_login(request):

    email = request.data.get("email")
    mobile = request.data.get("mobile")

    try:

        faculty = Faculty.objects.get(
            email=email,
            mobile=mobile
        )

        return Response({
            "success": True,
            "id": faculty.id,
            "name": faculty.name
        })

    except Faculty.DoesNotExist:

        return Response({
            "success": False,
            "message": "Invalid Faculty"
        })


# =====================================================
# DASHBOARD (OLD - WILL BE SKIPPED)
# =====================================================

@api_view(["GET"])
def dashboard(request):

    department = request.GET.get("department","All")

    if department == "All":

        total_students = Student.objects.count()

        present = Attendance.objects.filter(
            date=timezone.now().date()
        ).count()

    else:

        total_students = Student.objects.filter(
            department=department
        ).count()

        present = Attendance.objects.filter(
            date=timezone.now().date(),
            student__department=department
        ).count()

    absent = total_students - present

    percentage = 0

    if total_students > 0:

        percentage = round(
            (present / total_students) * 100,
            2
        )

    return Response({

        "total_students": total_students,

        "present": present,

        "absent": absent,

        "attendance": percentage

    })


# =====================================================
# STUDENT LIST
# =====================================================

@api_view(["GET"])
def student_list(request):

    department = request.GET.get("department","All")

    search = request.GET.get("search","")

    students = Student.objects.all()

    if department != "All":

        students = students.filter(
            department=department
        )

    if search:

        students = students.filter(
            name__icontains=search
        )

    data=[]

    today = timezone.now().date()

    for s in students:

        status="Absent"

        if Attendance.objects.filter(
            student=s,
            date=today
        ).exists():

            status="Present"

        data.append({

            "id":s.id,

            "name":s.name,

            "email":s.email,

            "mobile":s.mobile,

            "department":s.department,

            "semester":s.semester,

            "section":s.section,

            "status":status

        })

    return Response(data)


# =====================================================
# ADD STUDENT
# =====================================================

@api_view(["POST"])
def add_student(request):

    student = Student.objects.create(

        name=request.data["name"],

        email=request.data["email"],

        mobile=request.data["mobile"],

        department=request.data["department"],

        semester=request.data.get("semester",""),

        section=request.data.get("section","")

    )

    return Response({

        "success":True,

        "message":"Student Added",

        "id":student.id

    })


# =====================================================
# DELETE STUDENT
# =====================================================

@api_view(["DELETE"])
def delete_student(request,id):

    student=get_object_or_404(Student,id=id)

    student.delete()

    return Response({

        "success":True,

        "message":"Student Deleted"

    })

# =====================================================
# GENERATE QR (OLD - WILL BE SKIPPED)
# =====================================================

@api_view(["POST"])
def generate_qr(request):

    faculty_id = request.data.get("faculty_id")

    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Old active QR inactive
    QRHistory.objects.filter(status="active").update(
        status="inactive",
        expired_at=timezone.now()
    )

    token = str(uuid.uuid4())

    qr = QRHistory.objects.create(
        token=token,
        generated_by=faculty,
        status="active"
    )

    qr_folder = os.path.join(
        settings.MEDIA_ROOT,
        "attendance_qr"
    )

    os.makedirs(qr_folder, exist_ok=True)

    img = qrcode.make(token)

    filename = f"{token}.png"

    filepath = os.path.join(
        qr_folder,
        filename
    )

    img.save(filepath)

    qr.qr_image = f"attendance_qr/{filename}"
    qr.save()

    return Response({

        "success":True,

        "message":"QR Generated",

        "token":token,

        "image":settings.MEDIA_URL + qr.qr_image.name

    })


# =====================================================
# ACTIVE QR
# =====================================================

@api_view(["GET"])
def active_qr(request):

    qr = QRHistory.objects.filter(
        status="active"
    ).order_by("-created_at").first()

    if not qr:

        return Response({

            "success":False,

            "message":"No Active QR"

        })

    return Response({

        "success":True,

        "id":qr.id,

        "token":str(qr.token),

        "status":qr.status,

        "created_at":qr.created_at,

        "image":settings.MEDIA_URL + qr.qr_image.name

    })


# =====================================================
# QR HISTORY
# =====================================================

# @api_view(["GET"])
# def qr_history(request):

#     history = QRHistory.objects.order_by("-created_at")

#     data=[]

#     for q in history:

#         data.append({

#             "id":q.id,

#             "token":str(q.token),

#             "status":q.status,

#             "created_at":q.created_at,

#             "expired_at":q.expired_at,

#             "image":settings.MEDIA_URL + q.qr_image.name

#             if q.qr_image else None

#         })

#     return Response(data)

# @api_view(["GET"])
# def qr_history(request):
#     history = QRHistory.objects.order_by("-created_at")

#     data = []

#     for q in history:
#         # Pura (Absolute) URL banane ka logic
#         image_url = None
#         if q.qr_image:
#             image_url = request.build_absolute_uri(q.qr_image.url)

#         data.append({
#             "id": q.id,
#             "token": str(q.token),
#             "status": q.status,
#             "created_at": q.created_at,
#             "expired_at": q.expired_at,
#             "image": image_url  # Ab pura URL jayega
#         })

#     return Response(data)
# =====================================================
# VIEW SINGLE QR
# =====================================================

@api_view(["GET"])
def qr_detail(request,id):

    qr = get_object_or_404(QRHistory,id=id)

    return Response({

        "id":qr.id,

        "token":str(qr.token),

        "status":qr.status,

        "created_at":qr.created_at,

        "expired_at":qr.expired_at,

        "image":settings.MEDIA_URL + qr.qr_image.name

        if qr.qr_image else None

    })


# =====================================================
# DEACTIVATE QR
# =====================================================

# @api_view(["POST"])
# def deactivate_qr(request,id):

#     qr = get_object_or_404(QRHistory,id=id)

#     qr.status="inactive"

#     qr.expired_at=timezone.now()

#     qr.save()

#     return Response({

#         "success":True,

#         "message":"QR Deactivated"

#     })


# =====================================================
# DELETE QR
# =====================================================

@api_view(["DELETE"])
def delete_qr(request,id):

    qr = get_object_or_404(QRHistory,id=id)

    if qr.qr_image:

        path = qr.qr_image.path

        if os.path.exists(path):

            os.remove(path)

    qr.delete()

    return Response({

        "success":True,

        "message":"QR Deleted"

    })

# =====================================================
# SCAN QR & MARK ATTENDANCE
# =====================================================
# SCAN QR & MARK ATTENDANCE (MONGODB ATLAS B)
# ==========================================
@api_view(["POST"])
def scan_qr(request):
    try:
        email = request.data.get("email")
        token = request.data.get("token")
        student_lat = request.data.get("latitude")
        student_lon = request.data.get("longitude")
        today = datetime.now().strftime("%Y-%m-%d")

        db_B = collection_B.database
        attendance_coll = db_B["attendance"]

        # 1. Student check karein
        student = collection_B.find_one({"email": email})
        if not student:
            return Response({"success": False, "message": "Student Not Found in Database"})

        # 2. QR Active check karein
        qr = qr_coll.find_one({"token": token, "status": "active"})
        if not qr:
            return Response({"success": False, "message": "QR is Invalid or Expired!"})

        # 3. Location Check
        if qr.get("is_location_restricted"):
            if not student_lat or not student_lon:
                return Response({"success": False, "message": "Please enable Location/GPS to scan this QR."})
            
            distance = calculate_distance_in_meters(
                float(qr.get("latitude", 0)), float(qr.get("longitude", 0)), 
                float(student_lat), float(student_lon)
            )
            if distance > 10.0:
                return Response({"success": False, "message": f"You are out of class range! (Distance: {round(distance, 1)}m)"})

        # 4. Check already present
        existing = attendance_coll.find_one({"email": email, "date": today})
        if existing and existing.get("status") == "Present":
            return Response({"success": False, "message": "Attendance Already Marked for Today!"})

        # 5. Mark Present in MongoDB
        attendance_coll.update_one(
            {"email": email, "date": today},
            {"$set": {
                "name": student.get("name"),
                "email": email,
                "department": student.get("department") or student.get("program"),
                "date": today,
                "time": datetime.now().strftime("%H:%M:%S"),
                "status": "Present",
                "qr_token": token
            }},
            upsert=True
        )

        return Response({"success": True, "message": "Attendance Marked Successfully!"})
    except Exception as e:
        return Response({"success": False, "message": str(e)})
# =====================================================
# STUDENT ATTENDANCE HISTORY
# =====================================================
@api_view(["GET"])
def attendance_history(request):
    try:
        email = request.GET.get("email")
        db_B = collection_B.database
        attendance_coll = db_B["attendance"]

        # Sort by date descending (latest first)
        records = list(attendance_coll.find({"email": email}).sort("date", -1))
        
        history = []
        present = 0
        
        for r in records:
            status = r.get("status", "Absent")
            history.append({
                "date": r.get("date"),
                "time": r.get("time", "--:--"),
                "status": status
            })
            if status == "Present":
                present += 1
                
        total = len(records)
        absent = total - present
        percentage = round((present / total) * 100, 2) if total > 0 else 0

        return Response({
            "history": history,
            "present": present,
            "absent": absent,
            "percentage": percentage
        })
    except Exception as e:
        return Response({"history": [], "present": 0, "absent": 0, "percentage": 0})
# =====================================================
# EXPORT ALL CSV
# =====================================================

@api_view(["GET"])
def export_all_csv(request):

    department = request.GET.get("department","All")

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="Attendance_All.csv"'


    writer = csv.writer(response)

    writer.writerow([
        "Name",
        "Email",
        "Mobile",
        "Department",
        "Date",
        "Time",
        "Status"
    ])

    attendance = Attendance.objects.select_related(
        "student"
    )

    if department != "All":

        attendance = attendance.filter(
            student__department=department
        )

    for a in attendance:

        writer.writerow([
            a.student.name,
            a.student.email,
            a.student.mobile,
            a.student.department,
            a.date,
            a.time,
            a.status
        ])

    return response


# =====================================================
# EXPORT PRESENT CSV
# =====================================================

@api_view(["GET"])
def export_present_csv(request):

    department = request.GET.get("department","All")

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ]='attachment; filename="Present.csv"'


    writer = csv.writer(response)

    writer.writerow([
        "Name",
        "Department",
        "Date",
        "Time"
    ])

    attendance = Attendance.objects.select_related(
        "student"
    ).filter(
        status="Present"
    )

    if department!="All":

        attendance = attendance.filter(
            student__department=department
        )

    for a in attendance:

        writer.writerow([
            a.student.name,
            a.student.department,
            a.date,
            a.time
        ])

    return response


# =====================================================
# EXPORT ABSENT CSV
# =====================================================

@api_view(["GET"])
def export_absent_csv(request):

    department = request.GET.get("department","All")

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ]='attachment; filename="Absent.csv"'


    writer = csv.writer(response)

    writer.writerow([
        "Name",
        "Email",
        "Department"
    ])

    today = timezone.now().date()

    students = Student.objects.all()

    if department!="All":

        students = students.filter(
            department=department
        )

    for s in students:

        present = Attendance.objects.filter(
            student=s,
            date=today
        ).exists()

        if not present:

            writer.writerow([
                s.name,
                s.email,
                s.department
            ])

    return response


# =====================================================
# EXPORT SUMMARY
# =====================================================

@api_view(["GET"])
def export_summary_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ]='attachment; filename="Summary.csv"'


    writer = csv.writer(response)

    writer.writerow([
        "Department",
        "Total",
        "Present",
        "Absent",
        "Attendance %"
    ])

    departments = [
        "MCA",
        "BCA",
        "BBA"
    ]

    today = timezone.now().date()

    for d in departments:

        total = Student.objects.filter(
            department=d
        ).count()

        present = Attendance.objects.filter(
            student__department=d,
            date=today
        ).count()

        absent = total - present

        percentage = 0

        if total > 0:

            percentage = round(
                (present / total) * 100,
                2
            )

        writer.writerow([
            d,
            total,
            present,
            absent,
            percentage
        ])

    return response

# =====================================================
# ADDITIONAL OLD QR FUNCS (SKIPPED)
# =====================================================

import math
def calculate_distance_in_meters(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth ka radius meters mein
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


from pymongo import MongoClient
from django.conf import settings
import certifi

from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import certifi
from pymongo import MongoClient
import uuid

MONGO_URI_A = "mongodb+srv://sultanmulani65_db_user:45JKDAdNoXVu8eQ2@cluster0.xb7bodi.mongodb.net/?appName=Cluster0"
MONGO_URI_B = "mongodb+srv://rajupatelbasnijutha_db_user:rajupatelbasni@cluster0.ndesajd.mongodb.net/?appName=Cluster0"
# Crash-proof Database Connection with SSL Fixed (`certifi`)
try:
    client_A = MongoClient(
        MONGO_URI_A, 
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000
    )
    db_A = client_A["test"]
    collection_A = db_A["users"]
except Exception as e:
    print(f"⚠️ MongoDB Atlas A Connection Failed: {e}")
    collection_A = None

try:
    client_B = MongoClient(
        MONGO_URI_B, 
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000
    )
    db_B = client_B["Dpgu-Student-List"]
    faculty_coll = db_B["Faculty-List"]  # Naya Faculty Collection
    collection_B = db_B["Student-List"]
    qr_coll = db_B["qr_history"]
except Exception as e:
    print(f"⚠️ MongoDB Atlas B Connection Failed: {e}")
    collection_B = None

@api_view(["GET"])
def get_dpgu_faculties(request):
    if collection_B is None:
        return Response({"success": False, "faculties": []})
    
    # Faculty collection se data fetch karega
    data = list(faculty_coll.find({}, {"_id": 0}))
    return Response({"success": True, "faculties": data})
from pymongo import UpdateOne
# @api_view(["GET"])
# def get_atlas_a_students(request):
#     if collection_A is None:
#         return Response({"success": False, "students": []})
    
#     # {"_id": 0} lagana zaroori hai, warna MongoDB ki ObjectId frontend par crash hoti hai
#     data = list(collection_A.find({"role": "student"}, {"_id": 0}))
#     return Response({"success": True, "students": data})
@api_view(["GET"])
def get_atlas_a_students(request):
    try:
        # Force a completely fresh connection to avoid Render Worker crashes
        client_A = MongoClient(MONGO_URI_A, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=8000, connect=False)
        coll_A = client_A["test"]["users"]
        
        data = list(coll_A.find({"role": "student"}, {"_id": 0}))
        client_A.close() # Kaam khatam hote hi connection band karein
        
        return Response({"success": True, "students": data})
    except Exception as e:
        print("Atlas A Fetch Error:", str(e))
        return Response({"success": False, "students": [], "message": str(e)})
# ==========================================
# GET DPGU STUDENTS (With Today's Status)
# ==========================================
# @api_view(["GET"])
# def get_dpgu_students(request):
#     if collection_B is None:
#         return Response({"success": False, "students": []})
    
#     try:
#         # 1. MongoDB se saare students laayein
#         students = list(collection_B.find({}, {"_id": 0}))
        
#         # 2. Aaj ki date nikaalein aur Attendance collection se aaj ka data laayein
#         today = datetime.now().strftime("%Y-%m-%d")
#         attendance_coll = collection_B.database["attendance"]
#         todays_attendance = list(attendance_coll.find({"date": today}))
        
#         # 3. Fast lookup ke liye ek dictionary banayein (Email -> Status)
#         att_map = {att.get("email"): att.get("status") for att in todays_attendance}
        
#         # 4. Har student ke data mein uska aaj ka status jod dein
#         for student in students:
#             email = student.get("email")
#             # Agar record hai toh Present/Absent aayega, warna N/A rahega
#             student["status"] = att_map.get(email, "N/A") 
            
#         return Response({"success": True, "students": students})
        
#     except Exception as e:
#         print("Student List Error:", str(e))
#         return Response({"success": False, "students": [], "message": str(e)})

@api_view(["GET"])
def get_dpgu_students(request):
    if collection_B is None:
        return Response({"success": False, "students": []})
    
    try:
        # 1. MongoDB se saare students laayein
        students = list(collection_B.find({}, {"_id": 0}))
        
        # 2. 🔥 YAHAN CHANGE KIYA HAI 🔥
        # Frontend se URL mein aayi hui date uthayein (?date=YYYY-MM-DD)
        target_date = request.GET.get("date")
        
        # Agar date nahi aayi hai, tabhi aaj ki date lein
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")
            
        attendance_coll = collection_B.database["attendance"]
        
        # 3. Target date ka attendance data laayein
        todays_attendance = list(attendance_coll.find({"date": target_date}))
        
        # 4. Fast lookup ke liye ek dictionary banayein (Email -> Status)
        att_map = {att.get("email"): att.get("status") for att in todays_attendance}
        
        # 5. Har student ke data mein uska status jod dein
        for student in students:
            email = student.get("email")
            # Agar record hai toh Present/Absent aayega, warna N/A rahega
            student["status"] = att_map.get(email, "N/A") 
            
        return Response({"success": True, "students": students})
        
    except Exception as e:
        print("Student List Error:", str(e))
        return Response({"success": False, "students": [], "message": str(e)})

# 1. SYNC ATLAS A TO ATLAS B (With Update support)
# @api_view(["POST"])
# def sync_atlas_a_to_b(request):
#     if collection_A is None or collection_B is None:
#         return Response({"success": False, "message": "MongoDB is not connected."})

#     try:
#         synced_count = 0
#         updated_count = 0
        
#         # Atlas A se data laayein
#         external_students = list(collection_A.find({"role": "student"}))
        
#         for doc in external_students:
#             email = doc.get("email")
#             if not email:
#                 continue
            
#             doc.pop("_id", None) # Nayi ID banane ke liye purani _id remove karna zaroori hai
            
#             existing = collection_B.find_one({"email": email})
            
#             if existing:
#                 collection_B.update_one({"email": email}, {"$set": doc})
#                 updated_count += 1
#             else:
#                 collection_B.insert_one(doc)
#                 synced_count += 1
                
#         return Response({
#             "success": True, 
#             "message": f"Synced {synced_count} new, Updated {updated_count} students!"
#         })
#     except Exception as e:
#         return Response({"success": False, "message": str(e)})

# ------------------------------------------------------------------
# 2. UPDATE: SYNC ATLAS A TO B (SUPERFAST BULK WRITE LOGIC)
# ------------------------------------------------------------------
@api_view(["POST"])
def sync_atlas_a_to_b(request):
    try:
        # 1. Fresh connections banayein
        client_A = MongoClient(MONGO_URI_A, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=8000, connect=False)
        coll_A = client_A["test"]["users"]
        
        client_B = MongoClient(MONGO_URI_B, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=8000, connect=False)
        coll_B = client_B["Dpgu-Student-List"]["Student-List"]
        
        # 2. Atlas A se saara data ek sath fetch karein
        external_students = list(coll_A.find({"role": "student"}))
        
        # 3. Bulk Operations ki list banayein
        operations = []
        for doc in external_students:
            email = doc.get("email")
            if not email:
                continue
            
            doc.pop("_id", None) 
            
            # Upsert ka matlab hai: Agar email mile toh Update karo, na mile toh Insert (Naya banao)
            operations.append(UpdateOne({"email": email}, {"$set": doc}, upsert=True))

        # 4. Sirf 1 Single Request mein saara data database mein daal dein (SUPER FAST)
        if operations:
            coll_B.bulk_write(operations, ordered=False)

        # 5. Connections safely close karein
        client_A.close()
        client_B.close()
                
        return Response({
            "success": True, 
            "message": f"Successfully synced {len(operations)} students in a single batch!"
        })
    except Exception as e:
        print("Sync Error:", str(e))
        return Response({"success": False, "message": f"Connection Error: {str(e)}"})
# 2. API: Atlas B ka data Frontend pe bhejna
@api_view(["GET"])
def get_atlas_b_students(request):
    if collection_B is None:
        return Response({"students": [], "error": "Database B not connected"})
        
    students_cursor = collection_B.find().sort("createdAt", -1)
    students = []
    for doc in students_cursor:
        doc["_id"] = str(doc["_id"])
        students.append(doc)
    return Response({"students": students})


@api_view(["POST"])
def sync_mongo_data(request):
    try:
        # =====================================================
        # STEP 1: Atlas A se naye students Atlas B mein laayein (Safe)
        # =====================================================
        atlas_b_synced_count = 0
        if collection_A is not None and collection_B is not None:
            try:
                atlas_a_data = list(collection_A.find({"role": "student"}))
                for doc in atlas_a_data:
                    email = doc.get("email")
                    if not email:
                        continue
                    if not collection_B.find_one({"email": email}):
                        new_doc = doc.copy()
                        new_doc.pop("_id", None)
                        collection_B.insert_one(new_doc)
                        atlas_b_synced_count += 1
            except Exception as e:
                print(f"⚠️ Atlas A offline, skipping A->B sync: {e}")

        if collection_B is None:
            return Response({"success": False, "message": "MongoDB Atlas B is not connected."})

        db_b_root = collection_B.database
        students_coll = db_b_root["Student-List"]
        qr_backup_coll = db_b_root["qr_history_backup"]
        attendance_backup_coll = db_b_root["attendance_backup"]

        # =====================================================
        # STEP 2: Atlas B se data uthakar SQLite mein save karein
        # =====================================================
        sqlite_restored_count = 0
        all_b_students = list(students_coll.find())

        for doc in all_b_students:
            email = doc.get("email") or doc.get("mail") or doc.get("student_email")
            if not email:
                continue

            name = doc.get("name") or doc.get("studentName") or "Unknown"
            
            # Mobile exact mapping
            mobile = str(doc.get("mobile") or doc.get("phone") or doc.get("mobileno") or "")[:15]
            
            # Department exact mapping (MCA, BCA, BBA)
            raw_dept = str(doc.get("department") or doc.get("program") or "MCA").upper()
            department = "MCA" if "MCA" in raw_dept else ("BCA" if "BCA" in raw_dept else "BBA")

            # Semester aur Section exact mapping
            semester = str(doc.get("semester") or doc.get("academicYear") or doc.get("year") or "")
            section = str(doc.get("section") or "")

            # SQLite mein update_or_create
            Student.objects.update_or_create(
                email=email.strip().lower(),
                defaults={
                    "name": name,
                    "mobile": mobile,
                    "department": department,
                    "semester": semester,
                    "section": section
                }
            )
            sqlite_restored_count += 1

        # =====================================================
        # STEP 3: SQLite ka complete data Atlas B par STANDARD KEYS ke sath backup karein
        # =====================================================
        for s in Student.objects.all():
            students_coll.update_one(
                {"email": s.email},
                {
                    "$set": {
                        "name": s.name,
                        "email": s.email,
                        "mobile": s.mobile,         # Standard key for mobile
                        "department": s.department, # Standard key for department
                        "semester": s.semester,     # Standard key for semester
                        "section": s.section,       # Standard key for section
                        "role": "student",
                        "date_registered": str(s.created_at.date()) if s.created_at else ""
                    }
                },
                upsert=True
            )

        # 3.B: QR History Backup
        qr_count = 0
        for qr in QRHistory.objects.all():
            qr_backup_coll.update_one(
                {"token": str(qr.token)},
                {"$set": {
                    "token": str(qr.token),
                    "status": qr.status,
                    "created_at": str(qr.created_at),
                    "expired_at": str(qr.expired_at) if qr.expired_at else None,
                    "is_location_restricted": qr.is_location_restricted,
                    "latitude": qr.latitude,
                    "longitude": qr.longitude
                }},
                upsert=True
            )
            qr_count += 1

        # 3.C: Attendance Backup
        att_count = 0
        for att in Attendance.objects.all():
            attendance_backup_coll.update_one(
                {"student_email": att.student.email, "date": str(att.date)},
                {"$set": {
                    "student_email": att.student.email,
                    "student_name": att.student.name,
                    "date": str(att.date),
                    "time": str(att.time),
                    "status": att.status,
                    "qr_token": str(att.qr.token) if att.qr else None
                }},
                upsert=True
            )
            att_count += 1

        return Response({
            "success": True,
            "message": f"Sync & Standardized Backup Success! Students: {sqlite_restored_count} synchronized."
        })

    except Exception as e:
        print(f"❌ Sync Error: {str(e)}")
        return Response({
            "success": False,
            "message": f"Sync Error: {str(e)}"
        })

@api_view(["GET"])
def get_faculties(request):
    faculties = Faculty.objects.all().values("id", "name", "email", "mobile")
    return Response(list(faculties))


# 3. CSV EXPORT HELPERS & APIs (SQLite / Untouched)
# =====================================================
def generate_csv_response(filename, queryset, is_attendance=True):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    writer = csv.writer(response)
    
    if is_attendance:
        writer.writerow(['Date', 'Name', 'Email', 'Department', 'Status'])
        for att in queryset:
            writer.writerow([att.date, att.student.name, att.student.email, att.student.department, att.status])
    else:
        # Master Student Database Format
        writer.writerow(['Name', 'Email', 'Mobile', 'Department', 'Semester'])
        for student in queryset:
            writer.writerow([student.name, student.email, student.mobile, student.department, student.semester])
            
    return response

@api_view(["GET"])
def export_daily(request):
    date_str = request.GET.get("date")
    query = Attendance.objects.filter(date=date_str)
    return generate_csv_response(f"daily_report_{date_str}", query)

@api_view(["GET"])
def export_weekly(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    query = Attendance.objects.filter(date__range=[start, end])
    return generate_csv_response(f"weekly_report_{start}_to_{end}", query)

@api_view(["GET"])
def export_monthly(request):
    month_str = request.GET.get("month") 
    if month_str:
        year, month = month_str.split("-")
        query = Attendance.objects.filter(date__year=year, date__month=month)
        return generate_csv_response(f"monthly_report_{month_str}", query)
    return Response({"error": "Invalid Month"}, status=400)

@api_view(["GET"])
def export_all(request):
    query = Student.objects.all()
    return generate_csv_response("master_student_database", query, is_attendance=False)



# =========================================================================
# 🔥 MONGODB ATLAS B ACTIVE FUNCTIONS (YEH PURANE WALE OVERWRITE KARENGE) 🔥
# =========================================================================
from bson import ObjectId
import base64
from io import BytesIO

# 1. SETUP FACULTY (Naya)
@api_view(["GET"])
def setup_faculty_collection(request):
    if collection_B is None:
        return Response({"success": False, "message": "MongoDB is not connected."})
        
    try:
        existing = faculty_coll.find_one({"email": "rajupatelbasni@gmail.com"})
        
        if existing:
            return Response({
                "success": True, 
                "message": "Faculty already exists in MongoDB Atlas B!"
            })

        faculty_data = {
            "name": "Raju Patel 2",
            "email": "rajupatelbasni@gmail.com",
            "mobile": "7742121117"
        }

        faculty_coll.insert_one(faculty_data)
        return Response({"success": True, "message": "Faculty-List collection created!"})
    except Exception as e:
        return Response({"success": False, "message": str(e)})


# 2. DASHBOARD STATS
# 2. DASHBOARD STATS
@api_view(["GET"])
def dashboard(request):
    if collection_B is None:
        return Response({"total_students": 0, "present": 0, "absent": 0, "attendance": 0})
        
    dept = request.GET.get("department", "All")
    # ERROR FIXED HERE: datetime.now() instead of datetime.datetime.now()
    today = datetime.now().strftime("%Y-%m-%d") 
    
    student_query = {}
    if dept != "All":
        student_query = {"$or": [{"department": dept}, {"program": dept}]}
    
    total_students = collection_B.count_documents(student_query)
    
    attendance_coll = collection_B.database["attendance"]
    att_query = {"date": today}
    if dept != "All":
        att_query["department"] = dept
        
    present = attendance_coll.count_documents({**att_query, "status": "Present"})
    absent = attendance_coll.count_documents({**att_query, "status": "Absent"})
    
    attendance_rate = int((present / total_students * 100)) if total_students > 0 else 0
    
    return Response({
        "total_students": total_students,
        "present": present,
        "absent": absent,
        "attendance": attendance_rate
    })

# 3. QR HISTORY
@api_view(["GET"])
def qr_history(request):
    if 'qr_coll' not in globals() or qr_coll is None:
        return Response([])
        
    qrs = list(qr_coll.find().sort("created_at", -1))
    
    for q in qrs:
        q["id"] = str(q.pop("_id"))
        
    return Response(qrs)

# 4. DEACTIVATE QR
@api_view(["POST"])
def deactivate_qr(request, id):
    try:
        qr_coll.update_one({"_id": ObjectId(id)}, {"$set": {"status": "inactive"}})
        return Response({"success": True, "message": "QR Deactivated"})
    except Exception as e:
        return Response({"success": False, "message": str(e)})

# 5. ACTIVATE QR
@api_view(["POST"])
def activate_qr(request, id):
    try:
        qr_coll.update_many({}, {"$set": {"status": "inactive"}})
        qr_coll.update_one({"_id": ObjectId(id)}, {"$set": {"status": "active"}})
        return Response({"success": True, "message": "QR Activated"})
    except Exception as e:
        return Response({"success": False, "message": str(e)})

# 6. GENERATE QR (Save to MongoDB Direct)
# 6. GENERATE QR (Save to MongoDB Direct)
@api_view(["POST"])
def generate_qr_code(request):
    try:
        # Frontend se data receive karein
        data = request.data
        is_restricted = data.get("is_location_restricted", False)
        fac_lat = data.get("latitude", None)
        fac_lon = data.get("longitude", None)

        token = str(uuid.uuid4())
        
        # QR Code Image Generate karein
        img = qrcode.make(token)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # MongoDB ke liye Data prepare karein
        qr_data = {
            "token": token,
            "qr_image_base64": qr_base64,
            "status": "active",
            "created_at": datetime.now().isoformat(), # <-- ERROR FIXED HERE
            "is_location_restricted": is_restricted,  # <-- ADDED LOCATION SUPPORT
            "latitude": fac_lat,
            "longitude": fac_lon
        }
        
        # Pehle purane QRs ko Inactive karo
        qr_coll.update_many({}, {"$set": {"status": "inactive"}})
        
        # Phir Naya QR insert karo
        qr_coll.insert_one(qr_data)
        
        return Response({
            "success": True, 
            "token": token, 
            "qr_image": f"data:image/png;base64,{qr_base64}"
        })
    except Exception as e:
        # Terminal mein exact error print karne ke liye
        print("QR Generation Error:", str(e))
        return Response({"success": False, "detail": str(e)}) # 'detail' key added for frontend alert

# 7. REPORTS VIEW (On-Screen)
@api_view(["GET"])
def report_view(request):
    try:
        date = request.GET.get("date")
        dept = request.GET.get("department")

        db_B = collection_B.database
        attendance_coll = db_B["attendance"]

        student_query = {}
        if dept and dept != "All":
            student_query = {"$or": [{"department": dept}, {"program": dept}]}

        students = list(collection_B.find(student_query))
        attendance_records = list(attendance_coll.find({"date": date}))
        
        att_map = {att.get("email"): att.get("status") for att in attendance_records}

        results = []
        for s in students:
            email = s.get("email")
            results.append({
                "name": s.get("name"),
                "email": email,
                "department": s.get("department") or s.get("program", "N/A"),
                "status": att_map.get(email, "Absent") 
            })

        return Response({"success": True, "records": results})
    except Exception as e:
        return Response({"success": False, "message": str(e)})

# # 8. MARK ALL ABSENT (Bulk Action)
# @api_view(["POST"])
# def mark_all_absent(request):
#     try:
#         dept = request.data.get("department")
#         date = request.data.get("date")
        
#         db_B = collection_B.database
#         attendance_coll = db_B["attendance"]
        
#         student_query = {}
#         if dept and dept != "All":
#             student_query = {"$or": [{"department": dept}, {"program": dept}]}
            
#         students = list(collection_B.find(student_query))
#         count = 0
        
#         for s in students:
#             email = s.get("email")
#             if not email:
#                 continue
                
#             existing = attendance_coll.find_one({"email": email, "date": date})
            
#             if not existing:
#                 attendance_coll.insert_one({
#                     "email": email,
#                     "name": s.get("name"),
#                     "department": s.get("department") or s.get("program"),
#                     "date": date,
#                     "status": "Absent",
#                     "created_at": datetime.datetime.now().isoformat()
#                 })
#                 count += 1
                
#         return Response({"success": True, "message": f"Successfully marked {count} students as absent.", "count": count})
#     except Exception as e:
#         return Response({"success": False, "message": str(e)})


# section 22222222222222222222222


from datetime import datetime

@api_view(["POST"])
def mark_manual_present(request):
    try:
        email = request.data.get("email")
        date_input = request.data.get("date") # Frontend se aayi hui date
        
        # Agar frontend ne date bheji hai toh wo use karein, warna aaj ki date le lein
        today = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
        
        db_B = collection_B.database
        attendance_coll = db_B["attendance"]
        
        student = collection_B.find_one({"email": email})
        if not student:
            return Response({"success": False, "message": "Student not found in database."})
            
        # MongoDB me update (Ya naya insert)
        attendance_coll.update_one(
            {"email": email, "date": today},
            {"$set": {
                "name": student.get("name"),
                "email": email,
                "department": student.get("department") or student.get("program"),
                "date": today,
                "time": datetime.now().strftime("%H:%M:%S"),
                "status": "Present",
                "qr_token": "Marked_by_Faculty_Manual" 
            }},
            upsert=True
        )
        # Message mein date bhi dikhayenge taaki confirm ho jaye
        return Response({"success": True, "message": f"{student.get('name')} marked Present for {today}."})
    except Exception as e:
        return Response({"success": False, "message": str(e)})
# ==========================================
# SEND BULK EMAILS (ABSENT STUDENTS)
# ==========================================

import requests
# ==========================================
# SEND BULK EMAILS (ABSENT STUDENTS) - INTEGRATED WITH BREVO
# ==========================================
# ==========================================
# SEND BULK EMAILS (WITH QR ATTACHMENT & DYNAMIC MESSAGE)
# ==========================================
@api_view(["POST"])
def send_absent_emails(request):
    try:
        # Frontend se data receive karein
        emails = request.data.get("emails", [])
        include_qr = request.data.get("include_qr", False)
        message_text = request.data.get("message", "") # Custom ya Prebuilt message
        
        # 🔥 YAHAN CHANGE KIYA: Frontend se aayi hui subject line receive ki
        subject_text = request.data.get("subject", "") 
        
        if not emails:
            return Response({"success": False, "message": "No emails selected."})

        # Aapke Brevo Credentials
        import os
        API_KEY = os.getenv("BREVO_API_KEY")
        TEMPLATE_ID = 1  
        
        headers = {
            "accept": "application/json",
            "api-key": API_KEY,
            "content-type": "application/json"
        }

        db_B = collection_B.database
        students_coll = db_B["Student-List"]

        # =====================================
        # QR ATTACHMENT LOGIC
        # =====================================
        attachment_data = []
        if include_qr:
            active_qr = qr_coll.find_one({"status": "active"})
            if active_qr and active_qr.get("qr_image_base64"):
                attachment_data.append({
                    "content": active_qr["qr_image_base64"],
                    "name": "Attendance_QR.png"
                })

        success_count = 0

        for email in emails:
            student = students_coll.find_one({"email": email})
            firstname = student.get("name", "Student") if student else "Student"

            # 1. Contact Update
            contact_url = "https://api.brevo.com/v3/contacts"
            requests.post(contact_url, headers=headers, json={"email": email, "attributes": {"FIRSTNAME": firstname}, "updateEnabled": True}, timeout=5)

            # 2. Send Mail with attachment and params
            mail_url = "https://api.brevo.com/v3/smtp/email"
            mail_data = {
                "to": [{"email": email, "name": firstname}],
                "templateId": TEMPLATE_ID,
                "params": {
                    # Yeh parameter hum Brevo template ko bhej rahe hain
                    "custom_message": message_text 
                }
            }
            
            # 🔥 YAHAN CHANGE KIYA: Agar subject hai, toh payload me bhej diya
            if subject_text:
                mail_data["subject"] = subject_text
            
            # Agar QR bhejna hai toh attachment add karein
            if attachment_data:
                mail_data["attachment"] = attachment_data

            mail_response = requests.post(mail_url, headers=headers, json=mail_data, timeout=5)
            print("BREVO STATUS:", mail_response.status_code)
            print("BREVO RESPONSE:", mail_response.text)
            if mail_response.status_code in [200, 201, 202]:
                success_count += 1
        
        return Response({
            "success": True, 
            "message": f"Sent {success_count} emails successfully with your custom settings."
        })
        
    except Exception as e:
        print("Email Sending Error:", str(e))
        return Response({"success": False, "message": str(e)})

from pymongo import UpdateOne
from datetime import datetime # Dhyan rakhein ki import aisa hona chahiye


# ==========================================
# BULK ABSENT MARKING (ADVANCED & SAFE)
# ==========================================
@api_view(["POST"])
def mark_all_absent(request):
    try:
        # 1. Frontend se data receive karein
        date_input = request.data.get("date") 
        department = request.data.get("department", "All")

        if not date_input:
            return Response({"success": False, "message": "Date is missing in request."})

        # 2. DATE FORMAT FIXER: 
        # Agar date '2026-08-06T18:30:00Z' jaise format me aayi hai, toh sirf 'YYYY-MM-DD' nikaalein
        date_str = date_input
        if "T" in date_input:
            date_str = date_input.split("T")[0] 
        elif "/" in date_input:
            # Agar format DD/MM/YYYY hai, toh usko YYYY-MM-DD banayen
            try:
                date_str = datetime.strptime(date_input, "%d/%m/%Y").strftime("%Y-%m-%d")
            except:
                pass

        db_B = collection_B.database
        students_coll = db_B["Student-List"]
        attendance_coll = db_B["attendance"]

        # 3. Department filter
        student_query = {}
        if department != "All":
            student_query = {"$or": [{"department": department}, {"program": department}]}
        
        all_students = list(students_coll.find(student_query))
        
        if not all_students:
            return Response({"success": False, "message": f"No students found in {department} department!"})

        # 4. Jo bachhe PEHLE SE PRESENT hain, unhe dhoondhein
        already_present = list(attendance_coll.find({"date": date_str, "status": "Present"}))
        present_emails = [doc.get("email") for doc in already_present]

        operations = []

        for student in all_students:
            email = student.get("email")
            
            # Agar pehle se present hai, toh usko list me mat daalo (SKIP)
            if not email or email in present_emails:
                continue

            # Baaki sabko Absent lagane ki list me add karo
            operations.append(
                UpdateOne(
                    {"email": email, "date": date_str},
                    {"$set": {
                        "name": student.get("name", "Unknown"),
                        "email": email,
                        "department": student.get("department") or student.get("program") or "Unknown",
                        "date": date_str, # Perfect YYYY-MM-DD format save hoga
                        "time": "-",
                        "status": "Absent",
                        "qr_token": "System_Bulk_Absent"
                    }},
                    upsert=True
                )
            )

        # 5. Database mein Bulk Write karo
        if operations:
            attendance_coll.bulk_write(operations, ordered=False)

        # 6. EXACT REPORT BHEJEIN
        return Response({
            "success": True, 
            "message": f"Date: {date_str} | Found: {len(all_students)} Students | Skipped (Present): {len(present_emails)} | Marked Absent: {len(operations)}"
        })

    except Exception as e:
        print("Bulk Absent Error:", str(e))
        return Response({"success": False, "message": f"Backend Error: {str(e)}"})



import base64
import numpy as np
import cv2
import face_recognition


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def base64_to_image(base64_string):
    """Frontend se aayi hui base64 photo ko OpenCV image me convert karta hai"""
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula - Do GPS coordinates ke beech ka distance (meters me) nikalta hai"""
    R = 6371000 # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ==========================================
# API 1: FACE REGISTRATION
# ==========================================
@api_view(["POST"])
def register_face(request):
    try:
        email = request.data.get("email")
        image_b64 = request.data.get("image")
        
        db_B = collection_B.database
        students_coll = db_B["Student-List"]
        
        # 1. Convert Image
        img = base64_to_image(image_b64)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # ==========================================
        # 🔥 STRICT QUALITY GATES FOR REGISTRATION 🔥
        # ==========================================
        # A. Blur Check (Laplacian Variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 25.0:  # Very strict threshold for base photo
            return Response({"success": False, "message": "Photo is blurry. Please wipe your camera and keep steady."})
            
        # B. Lighting Check
        mean_brightness = np.mean(gray)
        if mean_brightness > 230:
            return Response({"success": False, "message": "Too much glare. Please move away from direct light."})
        if mean_brightness < 40:
            return Response({"success": False, "message": "Too dark. Please move to a well-lit area."})

        # 2. Get Face Encodings
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        live_encodings = face_recognition.face_encodings(rgb_img)
        
        if len(live_encodings) == 0:
            return Response({"success": False, "message": "No face detected. Align your face inside the frame."})
            
        if len(live_encodings) > 1:
             return Response({"success": False, "message": "Multiple faces detected. Please register alone."})
             
        face_encoding = live_encodings[0].tolist()

        # 3. Save to Database (Vector + Snapshot for Faculty to View)
        students_coll.update_one(
            {"email": email},
            {"$set": {
                "face_encoding": face_encoding,
                "face_registered": True,
                "face_snapshot": image_b64  # Optional: Saving snapshot to view in Faculty Dashboard
            }}
        )
        
        return Response({"success": True, "message": "Face Auto-Captured Successfully!"})

    except Exception as e:
        print("Registration Error:", str(e))
        return Response({"success": False, "message": str(e)})


def calculate_distance_points(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5

def get_ear(eye_points):
    # eye_points is a list of 6 (x,y) coordinates of the eye
    A = calculate_distance_points(eye_points[1], eye_points[5])
    B = calculate_distance_points(eye_points[2], eye_points[4])
    C = calculate_distance_points(eye_points[0], eye_points[3])
    return (A + B) / (2.0 * C)
# ==========================================
# API 2: FACE ATTENDANCE (SCAN & VERIFY)
# ==========================================
@api_view(["POST"])
def mark_face_attendance(request):
    try:
        email = request.data.get("email")
        images_b64 = request.data.get("images", []) # Ab array of images aayega
        user_lat = request.data.get("lat")
        user_lon = request.data.get("lon")
        
        db_B = collection_B.database
        students_coll = db_B["Student-List"]
        settings_coll = db_B["Settings"]
        attendance_coll = db_B["attendance"]
        
        # 1. Check Geofence
        face_settings = settings_coll.find_one({"type": "face_settings"}) 
        if face_settings and face_settings.get("location_enforced"):
            campus_lat = float(face_settings.get("active_lat"))
            campus_lon = float(face_settings.get("active_lon"))
            if not user_lat or not user_lon:
                return Response({"success": False, "message": "Location access is required."})
            if calculate_distance(float(user_lat), float(user_lon), campus_lat, campus_lon) > 25:
                return Response({"success": False, "message": "Out of range! Must be within 25m of campus."})

        # 2. Get Student's Saved Encoding
        student = students_coll.find_one({"email": email})
        if not student or "face_encoding" not in student:
            return Response({"success": False, "message": "Face not registered."})
        saved_encoding = np.array(student["face_encoding"])

        if len(images_b64) < 2:
            return Response({"success": False, "message": "Need multiple frames for liveness."})

        # ==========================================
        # 🔥 AADHAAR-STYLE BLINK DETECTION (EAR) 🔥
        # ==========================================
        # ==========================================
        # 🔥 AADHAAR-STYLE BLINK & DISTANCE DETECTION 🔥
        # ==========================================
        ear_values = []
        best_live_encoding = None

        for img_b64 in images_b64:
            if not img_b64: continue
            img = base64_to_image(img_b64)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # 1. Face Size (Distance) Check 
            face_locations = face_recognition.face_locations(rgb_img)
            if not face_locations:
                continue
                
            top, right, bottom, left = face_locations[0]
            face_area = (bottom - top) * (right - left)
            
            # Agar chehra frame me bohot chhota hai (door rakha phone)
            if face_area < 12000: # Adjust this value if needed (12000 pixels means fairly close)
                return Response({"success": False, "message": "Face too far! Please move your face closer to the camera."})

            # Get Encodings
            live_encodings = face_recognition.face_encodings(rgb_img, known_face_locations=[face_locations[0]])
            if len(live_encodings) > 0:
                best_live_encoding = live_encodings[0]

            # Get Facial Landmarks (Eyes)
            landmarks_list = face_recognition.face_landmarks(rgb_img, face_locations=[face_locations[0]])
            if landmarks_list:
                landmarks = landmarks_list[0]
                left_eye = landmarks.get('left_eye')
                right_eye = landmarks.get('right_eye')
                if left_eye and right_eye:
                    ear = (get_ear(left_eye) + get_ear(right_eye)) / 2.0
                    ear_values.append(ear)

        # 2. Strict Liveness Logic (True Blink Check)
        if len(ear_values) >= 2:
            min_ear = min(ear_values)
            max_ear = max(ear_values)
            
            # Asli blink me aankh poori khulni chahiye (max_ear > 0.22) aur poori band honi chahiye (min_ear < 0.21)
            if min_ear > 0.14: 
                return Response({"success": False, "message": "Spoof Detected: Blink Your eyes Continuously."})
            
            if max_ear < 0.18:
                return Response({"success": False, "message": "Please open your eyes clearly."})
        else:
            return Response({"success": False, "message": "Keep your eyes clearly visible in the frame."})

        # 3. Match Face
        if best_live_encoding is None:
            return Response({"success": False, "message": "No clear face detected."})

        match = face_recognition.compare_faces([saved_encoding], best_live_encoding, tolerance=0.38)[0]
        if not match:
            return Response({"success": False, "message": "Face did not match."})

        # 4. Mark Attendance
        today = datetime.now().strftime("%Y-%m-%d")
        if attendance_coll.find_one({"email": email, "date": today, "status": "Present"}):
             return Response({"success": False, "message": "Attendance already marked for today."})
             
        attendance_coll.update_one(
            {"email": email, "date": today},
            {"$set": {
                "name": student.get("name"), "email": email,
                "department": student.get("department") or student.get("program"),
                "date": today, "time": datetime.now().strftime("%H:%M:%S"),
                "status": "Present", "qr_token": "Marked_using_Face_Scan"
            }},
            upsert=True
        )
        return Response({"success": True, "message": "✅ Attendance Marked Successfully!"})

    except Exception as e:
        return Response({"success": False, "message": str(e)})
    
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def check_face_registration(request):
    try:
        email = request.GET.get("email")
        if not email:
            return Response({"success": False, "is_registered": False})
            
        db_B = collection_B.database
        students_coll = db_B["Student-List"]
        
        student = students_coll.find_one({"email": email})
        
        # Check agar student ke document me 'face_registered' True hai
        is_registered = bool(student and student.get("face_registered") == True)
        
        return Response({"success": True, "is_registered": is_registered})
        
    except Exception as e:
        return Response({"success": False, "is_registered": False, "message": str(e)})



# ==========================================
# FACULTY: FACE SCAN SETTINGS API
# ==========================================

@api_view(["GET"])
def get_face_settings(request):
    try:
        db_B = collection_B.database
        settings_coll = db_B["Settings"]
        
        # Database se settings nikalna
        settings = settings_coll.find_one({"type": "face_settings"}, {"_id": 0})
        
        # Agar pehli baar load ho raha hai aur DB me kuch nahi hai, to default bhejenge
        if not settings:
            settings = {
                "location_enforced": False,
                "locations": [
                    {"id": 1, "title": "Main Campus (Default)", "lat": "26.2389", "lng": "73.0243", "isActive": True}
                ]
            }
            
        return Response({"success": True, "settings": settings})
        
    except Exception as e:
        return Response({"success": False, "message": str(e)})


@api_view(["POST"])
def update_face_settings(request):
    try:
        db_B = collection_B.database
        settings_coll = db_B["Settings"]
        
        location_enforced = request.data.get("location_enforced", False)
        locations = request.data.get("locations", [])
        
        # Active location dhoondhna taaki attendance lagte waqt fast check ho sake
        active_lat = None
        active_lon = None
        for loc in locations:
            if loc.get("isActive"):
                active_lat = loc.get("lat")
                active_lon = loc.get("lng")
                break
                
        # MongoDB me save/update karna
        settings_coll.update_one(
            {"type": "face_settings"},
            {"$set": {
                "location_enforced": location_enforced,
                "locations": locations,
                "active_lat": active_lat, # Direct access ke liye
                "active_lon": active_lon  # Direct access ke liye
            }},
            upsert=True
        )
        
        return Response({"success": True, "message": "Face settings updated successfully!"})
        
    except Exception as e:
        return Response({"success": False, "message": str(e)})