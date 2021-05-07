import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from django.db.models import Sum
from django.template.loader import get_template
from xhtml2pdf import pisa
from student_management_app.forms import AddStudentForm, EditStudentForm, StaffAccountsForm, StudentAccountsForm, AddStudentInvoicePaymentForm, AddIncomeForm, AddIncomeHeadForm, AddExpenditureForm, AddExpenditureHeadForm
from student_management_app.models import CustomUser, Staffs, AddIncomeHead, AddIncome, AddExpenditure, StaffAccounts, StaffAccountsPayment, AddExpenditureHead, Courses, Subjects, Students, StudentAccounts, SessionYearModel, StudentAccountsPayment, \
    FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport


def admin_home(request):
    student_count1=Students.objects.all().count()
    staff_count=Staffs.objects.all().count()
    subject_count=Subjects.objects.all().count()
    course_count=Courses.objects.all().count()
    total_income=StudentAccounts.object.aggregate(Sum('total_amount_student'))['total_amount_student__sum']
    total_expenditure=StaffAccounts.object.aggregate(Sum('total_amount_staff'))['total_amount_staff__sum']

    course_all=Courses.objects.all()
    course_name_list=[]
    subject_count_list=[]
    student_count_list_in_course=[]
    for course in course_all:
        subjects=Subjects.objects.filter(course_id=course.id).count()
        students=Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all=Subjects.objects.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        course=Courses.objects.get(id=subject.course_id.id)
        student_count=Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs=Staffs.objects.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids=Subjects.objects.filter(staff_id=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)
        expenditures=AddExpenditure.object.all()
        total_amount_staff=0
        for expenditure in expenditures:
            total_amount_staff=expenditure.amount+total_amount_staff

    students_all=Students.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        leaves=LeaveReportStudent.objects.filter(student_id=student.id,leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves+absent)
        student_name_list.append(student.admin.username)
        incomes=AddIncome.object.all()
        total_amount_student=0
        for income in incomes:
            total_amount_student=income.amount+total_amount_student


    return render(request,"hod_template/home_content.html",{"student_count":student_count1,"staff_count":staff_count,"subject_count":subject_count,"course_count":course_count,"course_name_list":course_name_list,"subject_count_list":subject_count_list,"student_count_list_in_course":student_count_list_in_course,"student_count_list_in_subject":student_count_list_in_subject,"subject_list":subject_list,"staff_name_list":staff_name_list,"attendance_present_list_staff":attendance_present_list_staff,"attendance_absent_list_staff":attendance_absent_list_staff,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student})

def add_staff(request):
    return render(request,"hod_template/add_staff_template.html")

def add_staff_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=2)
            user.staffs.address=address
            user.save()
            messages.success(request,"Successfully Added Staff")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request,"Failed to Add Staff")
            return HttpResponseRedirect(reverse("add_staff"))

def add_course(request):
    return render(request,"hod_template/add_course_template.html")

def add_course_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        course=request.POST.get("course")
        try:
            course_model=Courses(course_name=course)
            course_model.save()
            messages.success(request,"Successfully Added Course")
            return HttpResponseRedirect(reverse("add_course"))
        except:
            messages.error(request,"Failed To Add Course")
            return HttpResponseRedirect(reverse("add_course"))

def add_student(request):
    form=AddStudentForm()
    return render(request,"hod_template/add_student_template.html",{"form":form})

def add_student_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address=form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id=form.cleaned_data["course"]
            sex=form.cleaned_data["sex"]

            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)

            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                user.students.address=address
                course_obj=Courses.objects.get(id=course_id)
                user.students.course_id=course_obj
                session_year=SessionYearModel.object.get(id=session_year_id)
                user.students.session_year_id=session_year
                user.students.gender=sex
                user.students.profile_pic=profile_pic_url
                user.save()
                messages.success(request,"Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))
            except:
                messages.error(request,"Failed to Add Student")
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form=AddStudentForm(request.POST)
            return render(request, "hod_template/add_student_template.html", {"form": form})


#Student_Accounts


def student_generate_invoice(request):
    form=StudentAccountsForm()
    return render(request,"hod_template/student_generate_invoice_template.html",{"form":form})

#Student_Accounts_Save

def student_invoice_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=StudentAccountsForm(request.POST)
        if form.is_valid():
            session_year_id=form.cleaned_data["session_year_id"]
            student=form.cleaned_data['student']
            balance=form.cleaned_data['balance']
            fee_type=form.cleaned_data['fee_type']
            account_number=form.cleaned_data['account_number']
            bank_name=form.cleaned_data['bank_name']
            amount=form.cleaned_data['amount']
            total_amount_student=balance+amount
            balance_left=total_amount_student
            try:
                session_year=SessionYearModel.object.get(id=session_year_id)
                student_id=CustomUser.objects.get(id=student)
                invoice=StudentAccounts(student=student_id,session_year_id=session_year,balance=balance,fee_type=fee_type,account_number=account_number,bank_name=bank_name,amount=amount,total_amount_student=total_amount_student,balance_left=balance_left)
                invoice.save()
                messages.success(request,"Successfully Added Student Invoice")
                return HttpResponseRedirect(reverse("student_generate_invoice"))
            except:
                messages.error(request,"Failed to Add Student Invoice")
                return HttpResponseRedirect(reverse("student_generate_invoice"))
        else:
            form=StudentAccountsForm(request.POST)
            return render(request, "hod_template/student_generate_invoice_template.html", {"form": form})



#Student_Accounts_list///Invoices_List
def student_invoice_list(request):
    invoices=StudentAccounts.object.all()
    return render(request,"hod_template/student_invoice_list_template.html",{"invoices":invoices})



def delete_student_invoice(request,invoice_id):
    StudentAccounts.object.get(id=invoice_id).delete()
    invoices=StudentAccounts.object.all()
    return render(request,"hod_template/student_invoice_list_template.html",{"invoices":invoices})


def add_subject(request):
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/add_subject_template.html",{"staffs":staffs,"courses":courses})

def add_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name=request.POST.get("subject_name")
        course_id=request.POST.get("course")
        course=Courses.objects.get(id=course_id)
        staff_id=request.POST.get("staff")
        staff=CustomUser.objects.get(id=staff_id)

        try:
            subject=Subjects(subject_name=subject_name,course_id=course,staff_id=staff)
            subject.save()
            messages.success(request,"Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request,"Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))


def manage_staff(request):
    staffs=Staffs.objects.all()
    return render(request,"hod_template/manage_staff_template.html",{"staffs":staffs})

def manage_student(request):
    students=Students.objects.all()
    return render(request,"hod_template/manage_student_template.html",{"students":students})

def accounts(request):
    return render(request,"hod_template/accounts_template.html")

def add_staffAccount(request):
    return render(request,"hod_template/add_staffAccount_template.html")

def staff_generate_invoice(request):
    return render(request,"hod_template/staff_generate_invoice_template.html")

def manage_course(request):
    courses=Courses.objects.all()
    return render(request,"hod_template/manage_course_template.html",{"courses":courses})

def manage_subject(request):
    subjects=Subjects.objects.all()
    return render(request,"hod_template/manage_subject_template.html",{"subjects":subjects})

def edit_staff(request,staff_id):
    staff=Staffs.objects.get(admin=staff_id)
    return render(request,"hod_template/edit_staff_template.html",{"staff":staff,"id":staff_id})

def edit_staff_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id=request.POST.get("staff_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address=request.POST.get("address")

        try:
            user=CustomUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()

            staff_model=Staffs.objects.get(admin=staff_id)
            staff_model.address=address
            staff_model.save()
            messages.success(request,"Successfully Edited Staff")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))
        except:
            messages.error(request,"Failed to Edit Staff")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))

def edit_student(request,student_id):
    request.session['student_id']=student_id
    student=Students.objects.get(admin=student_id)
    form=EditStudentForm()
    form.fields['email'].initial=student.admin.email
    form.fields['first_name'].initial=student.admin.first_name
    form.fields['last_name'].initial=student.admin.last_name
    form.fields['username'].initial=student.admin.username
    form.fields['address'].initial=student.address
    form.fields['course'].initial=student.course_id.id
    form.fields['sex'].initial=student.gender
    form.fields['session_year_id'].initial=student.session_year_id.id
    return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

def edit_student_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id=request.session.get("student_id")
        if student_id==None:
            return HttpResponseRedirect(reverse("manage_student"))

        form=EditStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id = form.cleaned_data["course"]
            sex = form.cleaned_data["sex"]

            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None


            try:
                user=CustomUser.objects.get(id=student_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email
                user.save()

                student=Students.objects.get(admin=student_id)
                student.address=address
                session_year = SessionYearModel.object.get(id=session_year_id)
                student.session_year_id = session_year
                student.gender=sex
                course=Courses.objects.get(id=course_id)
                student.course_id=course
                if profile_pic_url!=None:
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request,"Successfully Edited Student")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
            except:
                messages.error(request,"Failed to Edit Student")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
        else:
            form=EditStudentForm(request.POST)
            student=Students.objects.get(admin=student_id)
            return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

#student_invoice_list_payment

def student_invoice_list_payment(request,invoice_id):
    invoice=StudentAccounts.object.get(id=invoice_id)
    return render(request,"hod_template/student_invoice_list_payment_template.html",{"invoice":invoice,"id":invoice_id})


#student_invoice_list_payment_save

def student_invoice_list_payment_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        invoice_id=request.POST.get("invoice_id")
        amount=request.POST.get("amount_paid")
        date=request.POST.get("date")
        comment=request.POST.get("comment")
        try:
            invoice=StudentAccounts.object.get(id=invoice_id)
            total_paid_till_now=int(invoice.total_paid)+int(amount)
            invoice.total_paid=total_paid_till_now
            total_remaining=int(invoice.total_amount_student)-int(amount)
            invoice.total_amount_student=total_remaining
            invoice.balance_left=total_remaining
            invoice.save()
            student_payment=StudentAccountsPayment(invoice_id=invoice_id,payment=amount,date=date,comment=comment)
            student_payment.save()
            messages.success(request,"Successfully Edited Invoice")
            return HttpResponseRedirect(reverse("student_invoice_list"))
        except:
            messages.error(request,"Failed to Edit Invoice")
            return HttpResponseRedirect(reverse("student_invoice_list"))


def student_invoice_list_payment_history(request,invoice_id):
    invoice=StudentAccounts.object.get(id=invoice_id)
    payment_history=StudentAccountsPayment.object.all().filter(invoice_id=invoice_id)
    return render(request,"hod_template/student_invoice_list_payment_history_template.html",{"payment_history":payment_history,"invoice":invoice,"id":invoice_id})




def add_income_head(request):
    return render(request,"hod_template/add_income_head_template.html")


def add_income_head_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        income_name=request.POST.get("income_name")
        comment=request.POST.get("comment")

        try:
            income_data=AddIncomeHead(income_head=income_name,comment=comment)
            income_data.save()

            messages.success(request,"Successfully Income Head Added")
            return HttpResponseRedirect(reverse("add_income_head"))
        except:
            messages.error(request,"Failed to Add Income Head")
            return HttpResponseRedirect(reverse("add_income_head"))


def income_heads(request):
    income_heads_all=AddIncomeHead.object.all()
    return render(request,"hod_template/income_heads_template.html",{"income_heads_all":income_heads_all})

def delete_income_head(request,income_head_id):
    AddIncomeHead.object.get(id=income_head_id).delete()
    income_heads_all=AddIncomeHead.object.all()
    return render(request,"hod_template/income_heads_template.html",{"income_heads_all":income_heads_all})

def edit_income_head(request, income_head_id):
    income_head=AddIncomeHead.object.get(id=income_head_id)
    return render(request,"hod_template/edit_income_head_template.html",{"income_head":income_head})


def edit_income_head_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        income_head_id=request.POST.get("income_head_id")
        income=request.POST.get("income")
        comment=request.POST.get("comment")

        try:
            edit_head=AddIncomeHead.object.get(id=income_head_id)
            edit_head.income_head=income
            edit_head.comment=comment
            edit_head.save()

            messages.success(request,"Successfully Edited Income Head")
            return HttpResponseRedirect(reverse("income_heads"))
        except:
            messages.error(request,"Failed to Edit Income Head")
            return HttpResponseRedirect(reverse("income_heads"))



def add_income(request):
    form=AddIncomeForm()
    return render(request,"hod_template/add_income_template.html",{"form":form})

def add_income_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddIncomeForm(request.POST)
        if form.is_valid():
            student=form.cleaned_data['student']
            income_head_name=form.cleaned_data['head_name']
            amount=form.cleaned_data['amount']
            comment=form.cleaned_data['comment']
            try:
                student_id=CustomUser.objects.get(id=student)
                income_head_selected=AddIncomeHead.object.get(id=income_head_name)
                add_income_to_db=AddIncome(student=student_id.username,income_head=income_head_selected.income_head,amount=amount,comment=comment)
                add_income_to_db.save()
                messages.success(request,"Successfully income added")
                return HttpResponseRedirect(reverse("add_income"))
            except:
                messages.error(request,"Failed to Add Income")
                return HttpResponseRedirect(reverse("add_income"))
        else:
            form=AddIncomeForm(request.POST)
            return render(request, "hod_template/add_income_template.html", {"form": form})


def income_details(request):
    incomes=AddIncome.object.all()
    total_cash=AddIncome.object.all()
    total_amount_student=0
    for cash in total_cash:
        total_amount_student=cash.amount+total_amount_student
    return render(request,"hod_template/income_details_template.html",{"incomes":incomes,"total_amount_student":total_amount_student})



def delete_income_detail(request,income_id):
    AddIncome.object.get(id=income_id).delete()
    incomes=AddIncome.object.all()
    total_cash=AddIncome.object.all()
    total_amount_student=0
    for cash in total_cash:
        total_amount_student=cash.amount+total_amount_student
    return render(request,"hod_template/income_details_template.html",{"incomes":incomes,"total_amount_student":total_amount_student})


def edit_income_detail(request,income_id):
    income_head=AddIncome.object.get(id=income_id)
    students=Students.objects.all()
    incomes=AddIncomeHead.object.all()
    return render(request,"hod_template/edit_income_detail_template.html",{"students":students,"incomes":incomes,"income_head":income_head})

def edit_income_detail_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        income_detail_id=request.POST.get("income_detail_id")
        student=request.POST.get("student")
        amount=request.POST.get("amount")
        income=request.POST.get("income")
        comment=request.POST.get("comment")

        try:
            detail=AddIncome.object.get(id=income_detail_id)
            detail.amount=amount
            detail.comment=comment
            studentss=CustomUser.objects.get(id=student)
            detail.student=studentss.username
            income=AddIncomeHead.object.get(id=income)
            detail.income_head=income.income_head
            detail.save()

            messages.success(request,"Successfully Edited Income Detail")
            return HttpResponseRedirect(reverse("income_details"))
        except:
            messages.error(request,"Failed to Edit Income Details")
            return HttpResponseRedirect(reverse("income_details"))

def get_pdf_page(request):
    incomes=AddIncome.object.all()
    data={"incomes":incomes}
    template=get_template("hod_template/pdf_template.html")
    data_p=template.render(data)
    response=BytesIO()
    pdfPage=pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")),response)
    if not pdfPage.err:
        return HttpResponse(response.getvalue(),content_type="applicaion/pdf")
    else:
        return HttpResponse("Error generating pdf")

def edit_subject(request,subject_id):
    subject=Subjects.objects.get(id=subject_id)
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/edit_subject_template.html",{"subject":subject,"staffs":staffs,"courses":courses,"id":subject_id})

def edit_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id=request.POST.get("subject_id")
        subject_name=request.POST.get("subject_name")
        staff_id=request.POST.get("staff")
        course_id=request.POST.get("course")

        try:
            subject=Subjects.objects.get(id=subject_id)
            subject.subject_name=subject_name
            staff=CustomUser.objects.get(id=staff_id)
            subject.staff_id=staff
            course=Courses.objects.get(id=course_id)
            subject.course_id=course
            subject.save()

            messages.success(request,"Successfully Edited Subject")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))
        except:
            messages.error(request,"Failed to Edit Subject")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))


def edit_course(request,course_id):
    course=Courses.objects.get(id=course_id)
    return render(request,"hod_template/edit_course_template.html",{"course":course,"id":course_id})

def edit_course_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id=request.POST.get("course_id")
        course_name=request.POST.get("course")

        try:
            course=Courses.objects.get(id=course_id)
            course.course_name=course_name
            course.save()
            messages.success(request,"Successfully Edited Course")
            return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))
        except:
            messages.error(request,"Failed to Edit Course")
            return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))


def manage_session(request):
    return render(request,"hod_template/manage_session_template.html")



def add_session_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            sessionyear=SessionYearModel(session_start_year=session_start_year,session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect(reverse("manage_session"))

#Staff_Accounts


def staff_generate_invoice(request):
    form=StaffAccountsForm()
    return render(request,"hod_template/staff_generate_invoice_template.html",{"form":form})

#Staff_Accounts_Save

def staff_invoice_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=StaffAccountsForm(request.POST)
        if form.is_valid():
            staff=form.cleaned_data['staff']
            balance=form.cleaned_data['balance']
            pay_type=form.cleaned_data['pay_type']
            amount=form.cleaned_data['amount']
            session_year_id=form.cleaned_data["session_year_id"]
            total_amount_staff=balance+amount
            balance_left=total_amount_staff
            try:
                session_year=SessionYearModel.object.get(id=session_year_id)
                staff_id=CustomUser.objects.get(id=staff)
                invoice=StaffAccounts(staff=staff_id,session_year_id=session_year,balance=balance,pay_type=pay_type,amount=amount,total_amount_staff=total_amount_staff,balance_left=balance_left)
                invoice.save()
                messages.success(request,"Successfully Added Staff")
                return HttpResponseRedirect(reverse("staff_generate_invoice"))
            except:
                messages.error(request,"Failed to Add Staff")
                return HttpResponseRedirect(reverse("staff_generate_invoice"))
        else:
            form=StaffAccountsForm(request.POST)
            return render(request, "hod_template/staff_generate_invoice_template.html", {"form": form})



#Staff_Accounts_list///Invoices_List

def staff_invoice_list(request):
    invoices=StaffAccounts.object.all()
    return render(request,"hod_template/staff_invoice_list_template.html",{"invoices":invoices})



def delete_staff_invoice(request,invoice_id):
    StaffAccounts.object.get(id=invoice_id).delete()
    invoices=StaffAccounts.object.all()
    return render(request,"hod_template/staff_invoice_list_template.html",{"invoices":invoices})

#staff_invoice_list_payment

def staff_invoice_list_payment(request,invoice_id):
    invoice=StaffAccounts.object.get(id=invoice_id)
    return render(request,"hod_template/staff_invoice_list_payment_template.html",{"invoice":invoice,"id":invoice_id})


#staff_invoice_list_payment_save

def staff_invoice_list_payment_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        invoice_id=request.POST.get("invoice_id")
        amount=request.POST.get("amount_paid")
        date=request.POST.get("date")
        comment=request.POST.get("comment")
        try:
            invoice=StaffAccounts.object.get(id=invoice_id)
            total_paid_till_now=int(invoice.total_paid)+int(amount)
            invoice.total_paid=total_paid_till_now
            total_remaining=int(invoice.total_amount_staff)-int(amount)
            invoice.total_amount_staff=total_remaining
            invoice.balance_left=total_remaining
            invoice.save()
            staff_payment=StaffAccountsPayment(invoice_id=invoice_id,payment=amount,date=date,comment=comment)
            staff_payment.save()
            messages.success(request,"Successfully Edited Subject")
            return HttpResponseRedirect(reverse("staff_invoice_list"))
        except:
            messages.error(request,"Failed to Edit Subject")
            return HttpResponseRedirect(reverse("staff_invoice_list"))


def staff_invoice_list_payment_history(request,invoice_id):
    invoice=StaffAccounts.object.get(id=invoice_id)
    payment_history=StaffAccountsPayment.object.all().filter(invoice_id=invoice_id)
    return render(request,"hod_template/staff_invoice_list_payment_history_template.html",{"payment_history":payment_history,"invoice":invoice,"id":invoice_id})




def add_expenditure_head(request):
    return render(request,"hod_template/add_expenditure_head_template.html")


def add_expenditure_head_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        expenditure_name=request.POST.get("expenditure_name")
        comment=request.POST.get("comment")

        try:
            expenditure_data=AddExpenditureHead(expenditure_head=expenditure_name,comment=comment)
            expenditure_data.save()

            messages.success(request,"Successfully Expenditure Head Added")
            return HttpResponseRedirect(reverse("add_expenditure_head"))
        except:
            messages.error(request,"Failed to Add Expenditure Head")
            return HttpResponseRedirect(reverse("add_expenditure_head"))


def expenditure_heads(request):
    expenditure_heads_all=AddExpenditureHead.object.all()
    return render(request,"hod_template/expenditure_heads_template.html",{"expenditure_heads_all":expenditure_heads_all})

def delete_expenditure_head(request,expenditure_head_id):
    AddExpenditureHead.object.get(id=expenditure_head_id).delete()
    expenditure_heads_all=AddExpenditureHead.object.all()
    return render(request,"hod_template/expenditure_heads_template.html",{"expenditure_heads_all":expenditure_heads_all})

def edit_expenditure_head(request, expenditure_head_id):
    expenditure_head=AddExpenditureHead.object.get(id=expenditure_head_id)
    return render(request,"hod_template/edit_expenditure_head_template.html",{"expenditure_head":expenditure_head})


def edit_expenditure_head_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        expenditure_head_id=request.POST.get("expenditure_head_id")
        expenditure=request.POST.get("expenditure")
        comment=request.POST.get("comment")

        try:
            edit_head=AddexpenditureHead.object.get(id=expenditure_head_id)
            edit_head.expenditure_head=expenditure
            edit_head.comment=comment
            edit_head.save()

            messages.success(request,"Successfully Edited Expenditure Head")
            return HttpResponseRedirect(reverse("expenditure_heads"))
        except:
            messages.error(request,"Failed to Edit Expenditure Head")
            return HttpResponseRedirect(reverse("expenditure_heads"))

def add_expenditure(request):
    form=AddExpenditureForm()
    return render(request,"hod_template/add_expenditure_template.html",{"form":form})

def add_expenditure_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddExpenditureForm(request.POST)
        if form.is_valid():
            staff=form.cleaned_data['staff']
            expenditure_head_name=form.cleaned_data['head_name']
            amount=form.cleaned_data['amount']
            comment=form.cleaned_data['comment']
            try:
                staff_id=CustomUser.objects.get(id=staff)
                expenditure_head_selected=AddExpenditureHead.object.get(id=expenditure_head_name)
                add_expenditure_to_db=AddExpenditure(staff=staff_id.username,expenditure_head=expenditure_head_selected.expenditure_head,amount=amount,comment=comment)
                add_expenditure_to_db.save()
                messages.success(request,"Successfully expenditure added")
                return HttpResponseRedirect(reverse("add_expenditure"))
            except:
                messages.error(request,"Failed to Add Expenditure")
                return HttpResponseRedirect(reverse("add_expenditure"))
        else:
            form=AddExpenditureForm(request.POST)
            return render(request, "hod_template/add_expenditure_template.html", {"form": form})


def expenditure_details(request):
    expenditures=AddExpenditure.object.all()
    total_cash=AddExpenditure.object.all()
    total_amount_staff=0
    for cash in total_cash:
        total_amount_staff=cash.amount+total_amount_staff
    return render(request,"hod_template/expenditure_details_template.html",{"expenditures":expenditures,"total_amount_staff":total_amount_staff})



def delete_expenditure_detail(request,expenditure_id):
    AddExpenditure.object.get(id=expenditure_id).delete()
    expenditures=AddExpenditure.object.all()
    total_cash=AddExpenditure.object.all()
    total_amount_staff=0
    for cash in total_cash:
        total_amount_staff=cash.amount+total_amount_staff
    return render(request,"hod_template/expenditure_details_template.html",{"expenditures":expenditures,"total_amount_staff":total_amount_staff})


def edit_expenditure_detail(request,expenditure_id):
    expenditure_head=AddExpenditure.object.get(id=expenditure_id)
    staffs=Staffs.objects.all()
    expenditures=AddExpenditureHead.object.all()
    return render(request,"hod_template/edit_expenditure_detail_template.html",{"staffs":staffs,"expenditures":expenditures,"expenditure_head":expenditure_head})

def edit_expenditure_detail_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        expenditure_detail_id=request.POST.get("expenditure_detail_id")
        staff=request.POST.get("staff")
        amount=request.POST.get("amount")
        expenditure=request.POST.get("expenditure")
        comment=request.POST.get("comment")

        try:
            detail=AddExpenditure.object.get(id=expenditure_detail_id)
            detail.amount=amount
            detail.comment=comment
            staffss=CustomUser.objects.get(id=staff)
            detail.staff=staffss.username
            expenditure=AddExpenditureHead.object.get(id=expenditure)
            detail.expenditure_head=expenditure.expenditure_head
            detail.save()

            messages.success(request,"Successfully Edited Expenditure Detail")
            return HttpResponseRedirect(reverse("expenditure_details"))
        except:
            messages.error(request,"Failed to Edit Expenditure Details")
            return HttpResponseRedirect(reverse("expenditure_details"))

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def staff_feedback_message(request):
    feedbacks=FeedBackStaffs.objects.all()
    return render(request,"hod_template/staff_feedback_template.html",{"feedbacks":feedbacks})

def student_feedback_message(request):
    feedbacks=FeedBackStudent.objects.all()
    return render(request,"hod_template/student_feedback_template.html",{"feedbacks":feedbacks})

@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def staff_leave_view(request):
    leaves=LeaveReportStaff.objects.all()
    return render(request,"hod_template/staff_leave_view.html",{"leaves":leaves})

def student_leave_view(request):
    leaves=LeaveReportStudent.objects.all()
    return render(request,"hod_template/student_leave_view.html",{"leaves":leaves})

def student_approve_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))

def student_disapprove_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def staff_approve_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def staff_disapprove_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def admin_view_attendance(request):
    subjects=Subjects.objects.all()
    session_year_id=SessionYearModel.object.all()
    return render(request,"hod_template/admin_view_attendance.html",{"subjects":subjects,"session_year_id":session_year_id})

@csrf_exempt
def admin_get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request,"hod_template/admin_profile.html",{"user":user})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
