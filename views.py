from django.http import HttpResponseRedirect
from django.shortcuts import render

from forms import SignUpOne

def get_name(request):
    if request.method == 'POST':
        form = SignUpOne(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/paymentset.html')

        else:
            form = SignUpOne()

        return render(request, 'signup.html', {'form': form})