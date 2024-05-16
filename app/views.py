from django.shortcuts import render
from django.http import HttpResponse
from allauth.account.views import SignupView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

from app.form import UserRegistrationForm
from app.utils import send_confirmation_mail

from .models import Announcement
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Response
from .models import Category

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .form import UserRegistrationForm 
from django.http import Http404
from .models import Question

from django.urls import reverse_lazy
from .models import Response

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def send_notification(user, message):
    send_mail(
        'Уведомление',
        message,
        'noreply@example.com',
        [user.email],
        fail_silently=False,
    )
class CustomSignupView(SignupView):
    def form_valid(self, form):
        user = form.save(self.request)
        self.send_confirmation_mail(user)
        return super().form_valid(form)

    def send_confirmation_mail(self, user):
        # Генерация токена и кодирования uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Составление ссылки для подтверждения
        confirm_url = f"http://yourdomain.com/accounts/confirm-email/{uid}/{token}/"
        
        # Рендеринг шаблона письма
        subject = 'Подтверждение регистрации'
        html_message = render_to_string('registration/confirmation_email.html', {'confirm_url': confirm_url, 'user': user})
        plain_message = strip_tags(html_message)
        from_email = 'from@example.com'
        to = user.email

        # Отправка письма
        send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    # Пример вызова функции после регистрации пользователя
    def register_user(request):
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False  # Деактивируем пользователя до подтверждения почты
                user.save()
                send_confirmation_mail(user)
                return HttpResponse('На вашу почту отправлено письмо для подтверждения регистрации')



User = get_user_model()

def confirm_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return HttpResponse('Ссылка для подтверждения недействительна или срок её действия истёк')


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

class ResponseAcceptView(View):
    def get(self, request, pk):
        response = get_object_or_404(Response, pk=pk)
        if response.announcement.author == request.user:
            # логика принятия отклика, например, изменить статус отклика
            response.status = 'accepted'
            response.save()
            # логика отправки уведомления пользователю, оставившему отклик
            send_notification(response.author, 'Ваш отклик принят!')
        return redirect('user_responses')

class ResponseDeleteView(DeleteView):
    model = Response
    success_url = reverse_lazy('user_responses')

    def get_queryset(self):
        return self.model.objects.filter(announcement__author=self.request.user)


class ResponseCreateView(CreateView):
    model = Response
    fields = ['text']
    template_name = 'responses/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.announcement = Announcement.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcement'] = Announcement.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.announcement_id = self.kwargs['announcement_id']
        self.send_response_notification(form.instance)
        return super().form_valid(form)

    @receiver(post_save, sender=Response)
    def send_response_notification(sender, instance, created, **kwargs):
        if created:
        # Логика отправки уведомления
            pass




class UserResponsesListView(ListView):
    model = Response
    template_name = 'responses/user_responses.html'
    context_object_name = 'responses'

    def get_queryset(self):
        return self.model.objects.filter(announcement__author=self.request.user)



class ResponseDeleteView(DeleteView):
    model = Response
    template_name = 'responses/confirm_delete.html'

    def get_queryset(self):
        return self.model.objects.filter(announcement__author=self.request.user)


class AcceptResponseView(View):
    def get(self, request, pk):
        response = get_object_or_404(Response, pk=pk)
        if response.announcement.author == request.user:
            # логика принятия отклика, например, изменить статус отклика
            response.status = 'accepted'
            response.save()
            # логика отправки уведомления пользователю, оставившему отклик
            send_notification(response.author, 'Ваш отклик принят!')
        return redirect('user_responses')

class ResponseDeleteView(DeleteView):
    model = Response
    success_url = reverse_lazy('user_responses')

    def get_queryset(self):
        return self.model.objects.filter(announcement__author=self.request.user)




class CategoryListView(ListView):
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'

def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/detail.html", {"question": question})

from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import Choice, Question


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Деактивируем пользователя до подтверждения почты
            user.save()
            send_confirmation_mail(user)
            return HttpResponse('На вашу почту отправлено письмо для подтверждения регистрации')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})