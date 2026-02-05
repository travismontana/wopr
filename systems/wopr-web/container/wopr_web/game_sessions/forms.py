from core.models import Game, Session, Player, SessionPlayer, SessionImage

from django import forms

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'shortname', 'description', 'max_players', 'min_players', 'url', 'note']

class GameSessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['game', 'description', 'note']

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['irl_name', 'handle', 'description', 'note']

class SessionPlayerForm(forms.ModelForm):
    class Meta:
        model = SessionPlayer
        fields = ['session', 'player',]
        widgets = {
            'session': forms.HiddenInput(),
        }    
    def clean(self):
        cleaned_data = super().clean()
        session = cleaned_data.get('session')
        player = cleaned_data.get('player')
        
        if SessionPlayer.objects.filter(session=session, player=player).exists():
            raise forms.ValidationError("This player is already in this session.")
        
        return cleaned_data

class SessionImageForm(forms.ModelForm):
    class Meta:
        model = SessionImage
        fields = ['session', 'image']
        widgets = {
            'session': forms.HiddenInput(),
        }