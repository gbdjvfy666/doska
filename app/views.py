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
from django.contrib.auth.mixins import LoginRequiredMixin
from .form import ResponseForm
from .form import AnnouncementForm, UserRegistrationForm
from .models import Announcement, Response, Category, Question, Choice
from .utils import send_confirmation_mail
from django.views.generic import ListView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Response
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect


User = get_user_model()

from django.core.mail import send_mail
from django.template.loader import render_to_string

def response_list(request):
    responses = Response.objects.filter(user=request.user)
    return render(request, 'app/response_list.html', {'responses': responses})


def send_response_notification_email(response):
    subject = 'Уведомление о новом отклике на ваше объявление'
    message = 'У вас новый отклик на объявление. Проверьте ваш профиль для получения подробностей.'
    html_message = render_to_string('response_email.html', {'response': response})
    recipient_list = [response.ad.author.email]
    send_mail(subject, message, None, recipient_list, html_message=html_message)


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
    success_url = '/app/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class AnnouncementUpdateView(UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcements/update.html'
    context_object_name = 'announcement'
    
    def get_success_url(self):
        return reverse('announcement_detail', kwargs={'pk': self.object.pk})

class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcements/list.html'
    context_object_name = 'announcements'

class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'announcements/detail.html'
    context_object_name = 'announcement'

from django.contrib.auth.mixins import LoginRequiredMixin

class ResponseCreateView(LoginRequiredMixin, CreateView):
    model = Response
    form_class = ResponseForm
    template_name = 'responses/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.announcement = get_object_or_404(Announcement, pk=self.kwargs['announcement_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('announcement-detail', kwargs={'pk': self.kwargs['announcement_id']})
    
class ResponseAcceptView(LoginRequiredMixin, UpdateView):
    model = Response
    fields = ['status']
    template_name = 'app/response_accept.html'
    success_url = reverse_lazy('user-responses')

    def form_valid(self, form):
        response = form.save(commit=False)
        response.status = 'accepted'
        response.save()

        # Отправка уведомления пользователю, оставившему отклик
        send_mail(
            'Your response has been accepted',
            f'Your response to the announcement "{response.announcement.title}" has been accepted.',
            settings.DEFAULT_FROM_EMAIL,
            [response.author.email],
            fail_silently=False,
        )

        return super().form_valid(form)

    def get_queryset(self):
        return Response.objects.filter(announcement__author=self.request.user)

class ResponseDeleteView(LoginRequiredMixin, DeleteView):
    model = Response
    success_url = reverse_lazy('user-responses')

    def get_queryset(self):
        return Response.objects.filter(announcement__author=self.request.user)

class UserResponsesListView(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'app/user_responses.html'
    context_object_name = 'responses'

    def get_queryset(self):
        return Response.objects.filter(announcement__author=self.request.user)

    def get_queryset(self):
        return Response.objects.filter(ad__author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ads'] = Ad.objects.filter(author=self.request.user)
        return context
    
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




from django.shortcuts import render, get_object_or_404, redirect
from .models import Ad  
from .form import AdForm

def edit_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('announcement-list', ad_id=ad.id)  
    else:
        form = AdForm(instance=ad)
    return render(request, 'app/edit_ad.html', {'form': form, 'ad': ad})

def mass_sender(request):
    if request.user in Category.subscribers.all():
        send_mail(
            subject=f'Hi {request.user}, we have some news for you!',
            message=f'{Post.all()[-1].text}',
            from_email='azizauauau@yandex.ru',
            recipient_list=['imfyashya@gmail.com'])
        



from django.shortcuts import render, get_object_or_404, redirect
from .models import Ad, Response
from .form import AdForm, ResponseForm
from django.contrib.auth.decorators import login_required

@login_required
def create_response(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.user = request.user
            response.ad = ad
            response.save()
            return redirect('ad_detail', ad_id=ad.id)  
    else:
        form = ResponseForm()
    return render(request, 'create_response.html', {'form': form, 'ad': ad})

def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    responses = ad.responses.all()
    return render(request, 'ad_detail.html', {'ad': ad, 'responses': responses})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Response

@login_required
def response_list(request):
    responses = Response.objects.filter(user=request.user)
    return render(request, 'responses/response_list.html', {'responses': responses})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Announcement, Response, Notification

@login_required
def response_management(request):
    announcements = Announcement.objects.filter(user=request.user)
    selected_announcement = request.GET.get('announcement')
    if selected_announcement:
        responses = Response.objects.filter(announcement__id=selected_announcement)
    else:
        responses = Response.objects.filter(announcement__in=announcements)

    context = {
        'announcements': announcements,
        'responses': responses,
    }
    return render(request, 'responses/response_management.html', context)

@login_required
def delete_response(request, response_id):
    response = get_object_or_404(Response, id=response_id, announcement__user=request.user)
    response.delete()
    messages.success(request, 'Response deleted successfully.')
    return redirect('response-management')

@login_required
def accept_response(request, response_id):
    response = get_object_or_404(Response, id=response_id, announcement__user=request.user)
    response.accepted = True
    response.save()
    Notification.objects.create(
        user=response.user,
        message=f'Your response to "{response.announcement.title}" has been accepted.'
    )
    messages.success(request, 'Response accepted successfully.')
    return redirect('response-management')