from django import forms
from django.forms.widgets import NumberInput

scoreboard_choices = (
    ('job_state_scbd', 'Job State SCBD'),
    ('ack_scbd', 'Ack SCBD')
)

class table_query(forms.Form):
    choose_scoreboard = forms.MultipleChoiceField(choices=scoreboard_choices, widget=forms.CheckboxSelectMultiple())
    start_time = forms.CharField(label='Start time')
    end_time = forms.CharField(label='End time')
    img_chosen = forms.CharField()
    interval = forms.IntegerField(widget=NumberInput(attrs={'type': 'range', 'min': '0', 'max': '60', 'step':'1'}))

