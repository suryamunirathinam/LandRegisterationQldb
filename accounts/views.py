from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Accounts_info
# Create your views here.
def Accounts(request):
    if request.method == 'POST':
        if 'register' in request.POST:
            emailid=request.POST.get('email')
            password1=request.POST.get('password')
            password2=request.POST.get('confirm_password')

            if password1 == password2:
                obj = Accounts_info(email=emailid,password=password1)
                obj.save()
                return redirect('Pages/')
            else:
                return render(request,'accounts.html',{'message':'Invalid credentials Try again !!'})
        elif 'login' in request.POST:
            emailid=request.POST.get('login_email')
            loginpass = request.POST.get('login_password')
            if Accounts_info.objects.filter(email__iexact=emailid,password__iexact=loginpass):
                return redirect('Pages/')
            else:
                return render(request,'accounts.html')

      
    else:
        return render(request,'accounts.html')
    

