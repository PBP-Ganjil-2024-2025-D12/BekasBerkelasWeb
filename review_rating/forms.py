from django.forms import ModelForm
from review_rating.models import ReviewRating
from django.utils.html import strip_tags

class ReviewForm(ModelForm) :
    class Meta :
        model = ReviewRating
        fields = ["review", "rating"]
        
    def clean_review(self) :
        review = self.cleaned_data["review"]
        return strip_tags(review)
    
    