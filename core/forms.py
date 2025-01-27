from django import forms
from django.core.mail.message import EmailMessage
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from .models import BlogComment, BlogPost


class MembroLoginForm(forms.Form):
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError("Login ou Senha inválido!")
        return self.cleaned_data


class ContatoForm(forms.Form):
    nome = forms.CharField(label=_('Nome'), max_length=100)
    email = forms.EmailField(label=_('E-mail'), max_length=100)
    subject = forms.CharField(label=_('Subject'), max_length=100)
    message = forms.CharField(label=_('Message'), max_length=500)

    def send_mail(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']

        n = _('Nome')
        e = _('E-mail')
        s = _('Subjetc')
        m = _('Message')

        conteudo = f'{n}: {nome}\n{e}: {email}\n{s}: {subject}\n{m}: {message}'

        mail = EmailMessage(
            subject=subject,
            body=conteudo,
            from_email='contato@gmail.com',
            to=['contato@sarcophagus.com',],
            headers={'Reply-To': email},
        )
        mail.send()


class BlogForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['titulo', 'conteudo', 'imagem']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Post Title'}),
            'conteudo': forms.Textarea(attrs={'placeholder': 'Post Content'}),
        }

    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        if not imagem:
            raise forms.ValidationError("An image is required for the post.")
        return imagem


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['comentario']  # Campos do formulário de comentário
        labels = {
            'comentario': 'Comment',  # Altera o rótulo para "Comment"
        }
