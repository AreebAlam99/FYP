from django import forms

from student_management_app.models import Courses, SessionYearModel, Staffs, Students, AddIncomeHead, AddExpenditureHead, StudentAccountsPayment, StaffAccountsPayment


class DateInput(forms.DateInput):
    input_type = "date"

class AddStudentForm(forms.Form):
    email=forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control","autocomplete":"off"}))
    password=forms.CharField(label="Password",max_length=50,widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name=forms.CharField(label="First Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name=forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    username=forms.CharField(label="Username",max_length=50,widget=forms.TextInput(attrs={"class":"form-control","autocomplete":"off"}))
    address=forms.CharField(label="Address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    course_list=[]
    try:
        courses=Courses.objects.all()
        for course in courses:
            small_course=(course.id,course.course_name)
            course_list.append(small_course)
    except:
        course_list=[]
    #course_list=[]

    session_list = []
    try:
        sessions = SessionYearModel.object.all()

        for ses in sessions:
            small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
            session_list.append(small_ses)
    except:
        session_list=[]

    gender_choice=(
        ("Male","Male"),
        ("Female","Female")
    )

    course=forms.ChoiceField(label="Course",choices=course_list,widget=forms.Select(attrs={"class":"form-control"}))
    sex=forms.ChoiceField(label="Sex",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id=forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}))

#student_accounts

class StudentAccountsForm(forms.Form):
    student_list=[]
    try:
        students=Students.objects.all()
        for student in students:
            student_name=(student.admin.id,student.admin.username)
            student_list.append(student_name)
    except:
        student_list=[]
    #student_list=[]

    session_list = []
    try:
        sessions = SessionYearModel.object.all()

        for ses in sessions:
            small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
            session_list.append(small_ses)
    except:
        session_list=[]
    student=forms.ChoiceField(label="Student",choices=student_list,widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id=forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
    balance=forms.IntegerField(label="Balance From Previous",widget=forms.NumberInput(attrs={"class":"form-control"}))
    fee_type=forms.CharField(label="Fee Type",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    amount=forms.IntegerField(label="Amount",widget=forms.NumberInput(attrs={"class":"form-control"}))
    account_number=forms.CharField(label="Account Number",max_length=100,widget=forms.TextInput(attrs={"class":"form-control"}))
    bank_name=forms.CharField(label="Bank Name",max_length=100,widget=forms.TextInput(attrs={"class":"form-control"}))



class AddIncomeForm(forms.Form):
    student_list=[]
    try:
        students=Students.objects.all()
        for student in students:
            student_name=(student.admin.id,student.admin.username)
            student_list.append(student_name)
    except:
        student_list=[]
    #student_list=[]

    income_head_list=[]
    try:
        income_heads=AddIncomeHead.object.all()
        for income in income_heads:
            income_head_name=(income.id,income.income_head)
            income_head_list.append(income_head_name)
    except:
        income_head_list=[]

    student=forms.ChoiceField(label="Student",choices=student_list,widget=forms.Select(attrs={"class":"form-control"}))
    head_name=forms.ChoiceField(label="Income Heads",choices=income_head_list,widget=forms.Select(attrs={"class":"form-control"}))
    amount=forms.IntegerField(label="Amount",widget=forms.NumberInput(attrs={"class":"form-control"}))
    comment=forms.CharField(label="Comment",widget=forms.TextInput(attrs={"class":"form-control"}))

class AddIncomeHeadForm(forms.Form):
    income_head=forms.CharField(label="Income Head",widget=forms.TextInput(attrs={"class":"form-control"}))
    comment=forms.CharField(label="Comment",widget=forms.TextInput(attrs={"class":"form-control"}))

class EditStudentForm(forms.Form):
    email=forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name=forms.CharField(label="First Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name=forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    username=forms.CharField(label="Username",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    address=forms.CharField(label="Address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))


    course_list=[]
    try:
        courses = Courses.objects.all()
        for course in courses:
            small_course=(course.id,course.course_name)
            course_list.append(small_course)
    except:
        course_list=[]

    session_list = []
    try:
        sessions = SessionYearModel.object.all()

        for ses in sessions:
            small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
            session_list.append(small_ses)
    except:
        pass
        #session_list = []

    gender_choice=(
        ("Male","Male"),
        ("Female","Female")
    )

    course=forms.ChoiceField(label="Course",choices=course_list,widget=forms.Select(attrs={"class":"form-control"}))
    sex=forms.ChoiceField(label="Sex",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id=forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}),required=False)

class StaffAccountsForm(forms.Form):
    staff_list=[]
    try:
        staffs=Staffs.objects.all()
        for staff in staffs:
            staff_name=(staff.admin.id,staff.admin.username)
            staff_list.append(staff_name)
    except:
        staff_list=[]
    #staff_list=[]

    session_list = []
    try:
        sessions = SessionYearModel.object.all()

        for ses in sessions:
            small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
            session_list.append(small_ses)
    except:
        session_list=[]
    staff=forms.ChoiceField(label="Staff",choices=staff_list,widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id=forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
    balance=forms.IntegerField(label="Balance From Previous",widget=forms.NumberInput(attrs={"class":"form-control"}))
    pay_type=forms.CharField(label="Pay Type",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    amount=forms.IntegerField(label="Amount",widget=forms.NumberInput(attrs={"class":"form-control"}))

class AddExpenditureForm(forms.Form):
    staff_list=[]
    try:
        staffs=Staffs.objects.all()
        for staff in staffs:
            staff_name=(staff.admin.id,staff.admin.username)
            staff_list.append(staff_name)
    except:
        staff_list=[]
    #staff_list=[]

    expenditure_head_list=[]
    try:
        expenditure_heads=AddExpenditureHead.object.all()
        for expenditure in expenditure_heads:
            expenditure_head_name=(expenditure.id,expenditure.expenditure_head)
            expenditure_head_list.append(expenditure_head_name)
    except:
        expenditure_head_list=[]

    staff=forms.ChoiceField(label="Staff",choices=staff_list,widget=forms.Select(attrs={"class":"form-control"}))
    head_name=forms.ChoiceField(label="Expenditure Heads",choices=expenditure_head_list,widget=forms.Select(attrs={"class":"form-control"}))
    amount=forms.IntegerField(label="Amount",widget=forms.NumberInput(attrs={"class":"form-control"}))
    comment=forms.CharField(label="Comment",widget=forms.TextInput(attrs={"class":"form-control"}))

class AddExpenditureHeadForm(forms.Form):
    expenditure_head=forms.CharField(label="Expenditure Head",widget=forms.TextInput(attrs={"class":"form-control"}))
    comment=forms.CharField(label="Comment",widget=forms.TextInput(attrs={"class":"form-control"}))


class AddStaffInvoicePaymentForm(forms.Form):
    invoice_id=forms.IntegerField(label="Amount",widget=forms.NumberInput(attrs={"class":"form-control"}))
    amount=forms.IntegerField(label="Amount",widget=forms.NumberInput(attrs={"class":"form-control"}))
    comments=forms.CharField(label="Comments",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    date=forms.DateField(label="Date",widget=forms.DateInput(attrs={"class":"form-control"}))

#for payment of specific invoice
class AddStudentInvoicePaymentForm(forms.Form):
    invoice_id=forms.IntegerField(label="Amount",widget=forms.NumberInput(attrs={"class":"form-control"}))
    amount=forms.IntegerField(label="Amount",widget=forms.NumberInput(attrs={"class":"form-control"}))
    comments=forms.CharField(label="Comments",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    date=forms.DateField(label="Date",widget=forms.DateInput(attrs={"class":"form-control"}))
