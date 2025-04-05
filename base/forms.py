<<<<<<< HEAD
from django.forms import ModelForm
from .models import *

class DiscussionForm(ModelForm):
    class Meta:
        model = Discussion
        fields = '__all__'
=======
from django.forms import ModelForm
from .models import *

class DiscussionForm(ModelForm):
    class Meta:
        model = Discussion
        fields = '__all__'
        exclude = ['host', 'participants']
>>>>>>> master
