from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from allauth.account.views import SignupView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse, reverse_lazy

from .form import UserRegistrationForm
from .models import Announcement, Response, Category, Question, Choice
from .utils import send_confirmation_mail


User = get_user_model()

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email confirmation
            user.save()
            send_confirmation_mail(user)
            return HttpResponse('На вашу почту отправлено письмо для подтверждения регистрации')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def confirm_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return HttpResponse('Invalid confirmation link or it has expired.')



class CustomSignupView(SignupView):
    def form_valid(self, form):
        user = form.save(self.request)
        self.send_confirmation_mail(user)
        return super().form_valid(form)

    def send_confirmation_mail(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirm_url = f"http://wwwww.com/accounts/confirm-email/{uid}/{token}/"
        subject = 'Confirm Your Registration'
        html_message = render_to_string('registration/confirmation_email.html', {'confirm_url': confirm_url, 'user': user})
        plain_message = strip_tags(html_message)
        from_email = 'from@example.com'
        to = user.email
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)


class AnnouncementCreateView(CreateView):
    model = Announcement
    fields = ['title', 'content', 'category', 'image', 'video_url']
    template_name = 'announcements/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class AnnouncementUpdateView(UpdateView):
    model = Announcement
    fields = ['title', 'content', 'category', 'image', 'video_url']
    template_name = 'announcements/update.html'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcements/list.html'
    context_object_name = 'announcements'

class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'announcements/detail.html'
    context_object_name = 'announcement'


class ResponseCreateView(CreateView):
    model = Response
    fields = ['text']
    template_name = 'responses/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.announcement_id = self.kwargs['announcement_id']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcement'] = Announcement.objects.get(pk=self.kwargs['announcement_id'])
        return context

class ResponseAcceptView(View):
    def get(self, request, pk):
        response = get_object_or_404(Response, pk=pk)
        if response.announcement.author == request.user:
            response.status = 'accepted'
            response.save()
            send_notification(response.author, 'Your response has been accepted!')
        return redirect('user_responses')

class ResponseDeleteView(DeleteView):
    model = Response
    success_url = reverse_lazy('user_responses')

    def get_queryset(self):
        return self.model.objects.filter(announcement__author=self.request.user)

class UserResponsesListView(ListView):
    model = Response
    template_name = 'responses/user_responses.html'
    context_object_name = 'responses'

    def get_queryset(self):
        return self.model.objects.filter(announcement__author=self.request.user)

class CategoryListView(ListView):
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "polls/detail.html", {"question": question, "error_message": "You didn't select a choice."})
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})


def send_notification(user, message):
    send_mail(
        'Notification',
        message,
        'noreply@example.com',
        [user.email],
        fail_silently=False,
    )

@receiver(post_save, sender=Response)
def send_response_notification(sender, instance, created, **kwargs):
    if created:
        send_notification(instance.author, 'You have received a new response.')
