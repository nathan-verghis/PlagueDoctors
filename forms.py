from django import forms

class SignUpOne(forms.Form):
    fname = forms.CharField(label='fname', max_length=100)
    lname = forms.CharField(label="lname", max_length=100)
    dob = forms.DateField(label="dob")
    email = forms.EmailField(label="email")
    password = forms.CharField(label="password", max_length=100)
    conpassword = forms.CharField(label="conpassword", max_length=100)

    print(fname)