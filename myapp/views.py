import csv

import joblib
import numpy as np
import pandas as pd

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from .forms import RegisterForm, CalendarEventForm, EnquiryForm
from .models import OtpToken, CustomUser, Prediction, CalendarEvent, Enquiry, Reply, Event, Contact
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from .models import Prediction
from django.db.models.functions import TruncDate
from django.db.models import Count
import json


def home(request):
    return render(request, 'index.html')


def home1(request):
    return render(request, 'index1.html')


@transaction.atomic
def signup(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! An OTP was sent to your Email")
            return redirect("verify-email", username=request.POST['username'])
    context = {"form": form}
    return render(request, "signup.html", context)


def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()

    if request.method == 'POST':
        # valid token
        if user_otp.otp_code == request.POST['otp_code']:

            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active = True
                user.save()
                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("signin")

            # expired token
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("verify-email", username=user.username)


        # invalid otp code
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("verify-email", username=user.username)

    context = {}
    return render(request, "verify_token.html", context)


def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]

        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))

            # email variables
            subject = "Email Verification"
            message = f"""
                        Hi {user.username}, here is your OTP {otp.otp_code} 
                        it expires in 5 minute, use the url below to redirect back to the website
                        {user.username}

                        """
            sender = "hemavathikrishnan4463@gmail.com"
            receiver = [user.email, ]

            # send email
            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )

            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("verify-email", username=user.username)

        else:
            messages.warning(request, "This email dosen't exist in the database")
            return redirect("resend-otp")

    context = {}
    return render(request, "resend_otp.html", context)


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home1")

        else:
            messages.warning(request, "Invalid credentials")
            return redirect("signin")

    return render(request, "login.html")


@login_required
def reset_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevents user from being logged out
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('reset_password')  # Redirect to prevent form re-submission
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'reset_password.html', {
        'form': form,
    })


@login_required
def admin_reset_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevents user from being logged out
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('admin_reset_password')  # Redirect to prevent form re-submission
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'admin_reset_password.html', {
        'form': form,
    })



# Load the model at the start to avoid loading it on each request
model = joblib.load("C:/hemavathi/ThyroidDisease/ThyroidDisease/xgb_model.sav")

@login_required
def predict(request):
    if request.method == "POST":
        # Safely convert form data to float or int, using default values if None
        age = float(request.POST.get('age', 0.0))
        sex = int(request.POST.get('sex', 0))
        on_thyroxine = int(request.POST.get('on_thyroxine', 0))
        query_on_thyroxine = int(request.POST.get('query_on_thyroxine', 0))
        on_antithyroid_meds = int(request.POST.get('on_antithyroid_meds', 0))
        sick = int(request.POST.get('sick', 0))
        pregnant = int(request.POST.get('pregnant', 0))
        thyroid_surgery = int(request.POST.get('thyroid_surgery', 0))
        I131_treatment = int(request.POST.get('I131_treatment', 0))
        query_hypothyroid = int(request.POST.get('query_hypothyroid', 0))
        query_hyperthyroid = int(request.POST.get('query_hyperthyroid', 0))
        lithium = int(request.POST.get('lithium', 0))
        goitre = int(request.POST.get('goitre', 0))
        tumor = int(request.POST.get('tumor', 0))
        hypopituitary = int(request.POST.get('hypopituitary', 0))
        psych = int(request.POST.get('psych', 0))
        TSH_measured = int(request.POST.get('TSH_measured', 0))
        TSH = float(request.POST.get('TSH', 0.0))
        T3_measured = int(request.POST.get('T3_measured', 0))
        T3 = float(request.POST.get('T3', 0.0))
        TT4_measured = int(request.POST.get('TT4_measured', 0))
        TT4 = float(request.POST.get('TT4', 0.0))
        T4U_measured = int(request.POST.get('T4U_measured', 0))
        T4U = float(request.POST.get('T4U', 0.0))
        FTI_measured = int(request.POST.get('FTI_measured', 0))
        FTI = float(request.POST.get('FTI', 0.0))
        TBG_measured = int(request.POST.get('TBG_measured', 0))
        TBG = float(request.POST.get('TBG', 0.0))

        # Convert TSH and TT4 to ng/mL (assuming the units)
        TSH_ngml = TSH * 0.05  # TSH assumed to be in µIU/mL
        TT4_ngml = TT4 * 10    # TT4 assumed to be in µg/dL

        # Load the model
        model = joblib.load('xgb_model.sav')

        # Prepare the input data for prediction
        input_data = np.array([age, sex, on_thyroxine, query_on_thyroxine,
                               on_antithyroid_meds, sick, pregnant, thyroid_surgery,
                               I131_treatment, query_hypothyroid, query_hyperthyroid,
                               lithium, goitre, tumor, hypopituitary, psych,
                               TSH_measured, TSH_ngml, T3_measured, T3, TT4_measured,
                               TT4_ngml, T4U_measured, T4U, FTI_measured, FTI,
                               TBG_measured, TBG], dtype=object)

        # Convert NumPy data types to native Python types
        input_data = input_data.tolist()

        # Make the prediction
        prediction = model.predict([input_data])

        # Convert the prediction result to a Python int/float if needed
        prediction = int(prediction[0]) if prediction.dtype == 'int64' else float(prediction[0])

        # Map prediction to string
        prediction_map = {
            0: ('Negative', ' This indicates that the person does not have any thyroid-related condition. Their thyroid function appears normal based on the data provided.'),
            1: ('Hyperthyroid', ' Hyperthyroidism is a condition where the thyroid gland is overactive and produces too much of the hormone thyroxine (T4). This can lead to symptoms such as weight loss, rapid heartbeat, and nervousness.'),
            2: ('Subclinical Hyperthyroid', '	Subclinical hyperthyroidism occurs when thyroid hormone levels are still within the normal range, but the thyroid-stimulating hormone (TSH) levels are abnormally low. It is often considered a mild or early stage of hyperthyroidism.'),
            3: ('Hypothyroid', ' Hypothyroidism is when the thyroid gland is underactive and does not produce enough hormones. This leads to symptoms like fatigue, weight gain, and cold sensitivity.'),
            4: ('Subclinical Hypothyroid', '	Subclinical hypothyroidism occurs when the TSH levels are high, but the thyroid hormones (T4 and T3) are still within the normal range. This can be an early or mild form of hypothyroidism.'),
            5: ('Miscellaneous and General Health', '	This category refers to people who have undergone treatment for thyroid-related conditions (e.g., medication, surgery, radioactive iodine treatment) and are in a post-treatment phase. It might indicate either stable thyroid levels after treatment or residual effects from treatment.'),
            6: ('Treatment and Post-Treatment Conditions', '	This is a broad category for cases that dont fit neatly into the above categories. It might include other non-specific thyroid-related conditions or general health observations that are not directly thyroid-related.')
        }
        prediction_str, statement = prediction_map.get(prediction, ("Unknown", "The result does not match any known category."))

        # Save the prediction to the database
        p = Prediction(
            user=request.user,
            age=age,
            sex=sex,
            on_thyroxine=on_thyroxine,
            query_on_thyroxine=query_on_thyroxine,
            on_antithyroid_meds=on_antithyroid_meds,
            sick=sick,
            pregnant=pregnant,
            thyroid_surgery=thyroid_surgery,
            I131_treatment=I131_treatment,
            query_hypothyroid=query_hypothyroid,
            query_hyperthyroid=query_hyperthyroid,
            lithium=lithium,
            goitre=goitre,
            tumor=tumor,
            hypopituitary=hypopituitary,
            psych=psych,
            TSH_measured=TSH_measured,
            TSH=TSH_ngml,
            T3_measured=T3_measured,
            T3=T3,
            TT4_measured=TT4_measured,
            TT4=TT4_ngml,
            T4U_measured=T4U_measured,
            T4U=T4U,
            FTI_measured=FTI_measured,
            FTI=FTI,
            TBG_measured=TBG_measured,
            TBG=TBG,
            result=prediction_str
        )
        p.save()

        # Redirect to the result page or pass the prediction to a template
        context = {
            'prediction': prediction_str,
            'statement': statement
        }

        return render(request, 'result.html', context)

    return render(request, 'predict.html')


def result(request):
    prediction = request.session.get('prediction', None)

    # Render the result.html with the prediction
    return render(request, 'result.html', {'prediction': prediction})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Access denied. Admins only.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'admin_login.html')


@login_required
def dashboard_view(request):
    if request.user.is_authenticated:
        # Load the dataset for dashboard statistics
        df = pd.read_csv("C:/hemavathi/ThyroidDisease/ThyroidDisease/dataset/df_resampled.csv")

        # Load the model
        model = joblib.load("xgb_model.sav")

        # Prepare data for accuracy calculation
        x = df[['age', 'sex', 'on_thyroxine', 'query_on_thyroxine',
                'on_antithyroid_meds', 'sick', 'pregnant', 'thyroid_surgery',
                'I131_treatment', 'query_hypothyroid', 'query_hyperthyroid', 'lithium',
                'goitre', 'tumor', 'hypopituitary', 'psych', 'TSH_measured', 'TSH',
                'T3_measured', 'T3', 'TT4_measured', 'TT4', 'T4U_measured', 'T4U',
                'FTI_measured', 'FTI', 'TBG_measured', 'TBG']]
        y = df[['target']]

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        y_pred = model.predict(x_test)

        accuracy = accuracy_score(y_test, y_pred)*100

        # Get dashboard statistics
        target = df['target'].sum()
        user = CustomUser.objects.count()
        prediction = Prediction.objects.count()
        schedule = CalendarEvent.objects.count()
        enquiry = Enquiry.objects.count()
        contact = Contact.objects.count()

        # Aggregate predictions by day
        daily_predictions = Prediction.objects.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

        # Convert queryset to a format suitable for Chart.js
        dates = [entry['date'].strftime('%Y-%m-%d') for entry in daily_predictions]  # Convert date to string
        counts = [entry['count'] for entry in daily_predictions]

        # Prepare context with all necessary data
        context = {
            'target': target,
            'user': user,
            'prediction': prediction,
            'schedule': schedule,
            'enquiry': enquiry,
            'accuracy': accuracy,  # Add accuracy to the context
            'dates': json.dumps(dates),
            'counts': json.dumps(counts),
            'enquiry_count':json.dumps(enquiry),
            'user_count': json.dumps(user),
            'contact': contact,
        }

        return render(request, 'dashboard.html', context)
    else:
        messages.error(request, "You need to log in to access the dashboard.")
        return redirect('/admin_login')


def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users':users})


def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
        messages.success(request, 'User successfully deleted.')
        return redirect('user_list')


@login_required()
def admin_prediction_list(request):
    # Fetch predictions from the database
    predictions = Prediction.objects.all()

    # Pass the predictions to the template
    context = {
        'predictions': predictions
    }

    return render(request, 'admin_prediction_list.html', context)

@login_required
def user_prediction_list(request):
    if not request.user.is_superuser:
        predictions = Prediction.objects.filter(user=request.user)
    else:
        return redirect('dashboard')  # Admins are redirected to their page
    return render(request, 'user_prediction_list.html', {'predictions': predictions})


@login_required
def delete_prediction(request, prediction_id):
    prediction = get_object_or_404(Prediction, id=prediction_id)
    if prediction.user != request.user:
        messages.error(request, 'You are not authorized to delete this prediction.')
        return redirect('user_prediction_list')
    if request.method == 'POST':
        prediction.delete()
        messages.success(request, 'Predicted data successfully deleted.')
        return redirect('user_prediction_list')

    return HttpResponseNotAllowed(['POST'])


def download_prediction(request, prediction_id):
    prediction = get_object_or_404(Prediction, id=prediction_id)

    # Create an HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="prediction_{prediction_id}.csv"'

    writer = csv.writer(response)
    # Write CSV headers
    writer.writerow([
        'ID', 'Age', 'Sex', 'On Thyroxine', 'On Antithyroid Meds', 'Sick', 'Pregnant',
        'Thyroid Surgery', 'I131 Treatment', 'Query Hypothyroid', 'Query Hyperthyroid',
        'Lithium', 'Goitre', 'Tumor', 'Hypopituitary', 'Psych', 'FTI Measured',
        'TSH Measured', 'T3 Measured', 'TT4 Measured', 'T4U Measured', 'TBG Measured',
        'TSH', 'T3', 'TT4', 'T4U', 'FTI', 'TBG', 'Result'
    ])
    # Write the data row
    writer.writerow([
        prediction.id, prediction.age, prediction.sex, prediction.on_thyroxine,
        prediction.on_antithyroid_meds, prediction.sick, prediction.pregnant,
        prediction.thyroid_surgery, prediction.I131_treatment, prediction.query_hypothyroid,
        prediction.query_hyperthyroid, prediction.lithium, prediction.goitre, prediction.tumor,
        prediction.hypopituitary, prediction.psych, prediction.FTI_measured, prediction.TSH_measured,
        prediction.T3_measured, prediction.TT4_measured, prediction.T4U_measured, prediction.TBG_measured,
        prediction.TSH, prediction.T3, prediction.TT4, prediction.T4U, prediction.FTI, prediction.TBG,
        prediction.result
    ])

    return response


def admin_download_prediction(request, prediction_id):
    # Fetch the prediction object
    prediction = get_object_or_404(Prediction, id=prediction_id)

    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="prediction_{prediction.id}.csv"'

    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['ID', 'User', 'Age', 'Sex', 'TSH', 'T3', 'TT4', 'T4U', 'FTI', 'TBG', 'Result', 'Created At'])

    # Check if user exists and fetch username
    username = prediction.user.username if prediction.user else 'No User'

    # Write the prediction data
    writer.writerow([prediction.id, username, prediction.age, prediction.sex,
                     prediction.TSH, prediction.T3, prediction.TT4, prediction.T4U,
                     prediction.FTI, prediction.TBG, prediction.result, prediction.created_at])

    return response


def event_page(request):
    if request.method == 'POST':
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.save()
            return redirect('event_page')  # Redirect to the desired page
    else:
        title = request.GET.get('title', '')
        start = request.GET.get('start', '')
        end = request.GET.get('end', '')
        location = request.GET.get('location', '')
        username = request.GET.get('username', '')

        initial_data = {
            'title': title,
            'start_time': start,
            'end_time': end,
            'location': location,
            'username': username,
        }

        event_id = request.GET.get('event_id', None)
        if event_id:
            event = get_object_or_404(CalendarEvent, id=event_id)
            initial_data.update({
                'title': event.title,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'location': event.location,
                'username': event.username,
            })
            form = CalendarEventForm(instance=event)
        else:
            form = CalendarEventForm(initial=initial_data)

    return render(request, 'event_page.html', {'form': form})


def get_events(request):
    events = CalendarEvent.objects.all()
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'start': localtime(event.start_time).isoformat(),  # Convert to local time
            'end': localtime(event.end_time).isoformat(),
            'description': event.description,
            'location': event.location,
            'username': event.username,
            'room': event.room,
            'doctor': event.doctor

        })
    return JsonResponse(event_list, safe=False)


# Update event details
@csrf_exempt
@require_http_methods(["POST"])
def update_event(request, event_id):
    try:
        event = CalendarEvent.objects.get(id=event_id)
        event.title = request.POST.get('title', event.title)
        event.start_time = request.POST.get('start', event.start_time)
        event.end_time = request.POST.get('end', event.end_time)
        event.description = request.POST.get('description', event.description)
        event.location = request.POST.get('location', event.location)
        event.save()
        return JsonResponse({'status': 'success'})
    except CalendarEvent.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Event not found'})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_event(request, event_id):
    try:
        event = CalendarEvent.objects.get(id=event_id)
        event.delete()
        return JsonResponse({'status': 'success'})
    except CalendarEvent.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Event not found'})


@login_required
def book_event_page(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        start = request.POST.get('start')
        end = request.POST.get('end')

        Event.objects.create(
            title=title,
            start=start,
            end=end,
            user=request.user  # Save the current user with the event
        )
        return redirect('user_booked_list')

    return render(request, 'book_schedule.html')


@login_required
def user_booked_list(request):
    events = Event.objects.filter(user=request.user).order_by('-start')
    calendar_events = CalendarEvent.objects.filter(username=request.user.username).order_by('-start_time')  # Adjust this filter if needed
    return render(request, 'user_booked_list.html', {'events': events, 'calendar_events': calendar_events})


def user_delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, "Event deleted successfully!")
    return redirect('user_booked_list')

@login_required()
def admin_booked_list(request):
   events = Event.objects.all()
   calendar_events = CalendarEvent.objects.all()
   return render(request, 'admin_booked_list.html', {'events': events, 'calendar_events': calendar_events})


def delete_appointment(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    event.deleted = True
    event.confirmed = False
    event.message = f'Appointment cancelled by Admin on {timezone.now().date()}. Due to appointment full'
    event.save()
    messages.success(request, 'Appointment deleted successfully.')
    return redirect('admin_booked_list')


@login_required
def confirm_appointment(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    event.confirmed = True
    event.message = f'Confirmed'
    event.save()
    messages.success(request, f'Appointment has been confirmed.')
    return redirect('admin_booked_list')


@login_required  # Ensure only logged-in users can access the form
def enquiry(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.user = request.user  # Link enquiry to the logged-in user
            enquiry.name = request.user.username  # Automatically set the username
            enquiry.email = request.user.email  # Automatically set the email
            enquiry.save()
            messages.success(request, 'Your enquiry has been submitted successfully!')
            return redirect('enquiry')  # Redirect after successful submission
    else:
        form = EnquiryForm()

    return render(request, 'enquiry.html', {'form': form})


@login_required()
def admin_enquiry_list(request):
   enquiries = Enquiry.objects.all()
   return render(request, 'admin_enquiry_list.html', {'enquiries': enquiries})


def reply_enquiry(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)

    if request.method == "POST":
        reply_message = request.POST.get('reply_message')

        if reply_message:
            enquiry.reply_message = reply_message
            enquiry.replied = True
            enquiry.save()
            messages.success(request, 'Reply sent successfully.')
        else:
            messages.error(request, 'Reply message cannot be empty.')

    return redirect('admin_enquiry_list')


@login_required
def user_enquiry_list(request):
    enquiries = Enquiry.objects.filter(user=request.user)
    return render(request, 'user_enquiry_list.html', {'enquiries': enquiries})


@login_required
def delete_enquiry(request, enquiry_id):
    if request.method == 'POST':
        enquiry = get_object_or_404(Enquiry, id=enquiry_id, user=request.user)
        enquiry.delete()
    return redirect('user_enquiry_list')


def get_user_data(request):
    total_users = CustomUser.objects.count()

    data = {
        'total_users': total_users
    }
    return JsonResponse(data)


def contact_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save the form data to the database
        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')

    return render(request, 'index.html')


def admin_email_list(request):
    contacts = Contact.objects.all()
    return render(request, 'admin_email_list.html', {'contacts':contacts})
