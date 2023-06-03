from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.core.exceptions import ValidationError
from recipes.models import Tag, Recipe


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit)
        self.instance = instance
        self.clean()
        return instance

    def clean(self):
        super().clean()
        if self.cleaned_data.get('ingredients'):
            raise ValidationError(
                'Рецепт должен иметь хотя бы один ингредиент.'
            )
