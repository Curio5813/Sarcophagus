from django import forms
from django.core.mail.message import EmailMessage


class ContatoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=100)
    email = forms.EmailField(label='E-mail', max_length=100)
    subject = forms.CharField(label='Subject', max_length=100)
    message = forms.CharField(label='Message', max_length=500)

    def send_mail(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']

        conteudo = f'Nome: {nome}\nE-mail: {email}\nSubject: {subject}\nMessage: {message}'

        mail = EmailMessage(
            subject=subject,
            body=conteudo,
            from_email='contato@gmail.com',
            to=['contato@sarcophagus.com',],
            headers={'Reply-To': email},
        )
        mail.send()

