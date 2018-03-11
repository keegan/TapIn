from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import AuthForm
# Create your views here.
def formRequest(request): 
	if request.method == "POST":
		form = AuthForm(request.POST);
		if form.isValid():
			#process data
			#return to another url v
			#return HTTPResponseDirect(insert url here)
	else:
		form = AuthForm()

	return render(request, "backui.html", {'form':form})