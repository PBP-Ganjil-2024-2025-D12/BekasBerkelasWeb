from django.forms import ModelForm
from forum.models import Question, Reply
from django.utils.html import strip_tags

class ForumForm(ModelForm) :
    class Meta :
        model = Question
        fields = ["title", "content", "car", "category"]
        
    def clean_title(self) :
        title = self.cleaned_data["title"]
        return strip_tags(title)
    
    def clean_content(self) :
        content = self.cleaned_data["content"]
        return strip_tags(content)
    
class ReplyForm(ModelForm) :
    class Meta :
        model = Reply
        fields = ["content"]
    
    def clean_content(self) :
        content = self.cleaned_data["content"]
        return strip_tags(content)