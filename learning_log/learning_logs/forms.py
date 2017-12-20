from django import forms

from learning_logs.models import Topic, Entry


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': 'topic_text'}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': 'entry_text'}
        widgets = {'text': forms.Textarea(attrs={'cols' : 80})}