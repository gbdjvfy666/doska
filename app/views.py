from django.shortcuts import render
from django.http import HttpResponse
from allauth.account.views import SignupView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.list import ListView

from .models import Announcement
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Response
from .models import Category

from django.http import Http404
from .models import Question

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class CustomSignupView(SignupView):
    def form_valid(self, form):
        user = form.save(self.request)
        self.send_confirmation_mail(user)
        return super().form_valid(form)

    def send_confirmation_mail(self, user):
        # Логика отправки письма с подтверждением
        pass



class AnnouncementCreateView(CreateView):
    model = Announcement
    fields = ['title', 'content', 'category']
    template_name = 'announcements/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AnnouncementUpdateView(UpdateView):
    model = Announcement
    fields = ['title', 'content', 'category']
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
        self.send_response_notification(form.instance)
        return super().form_valid(form)

    def send_response_notification(self, response):
        # Логика отправки уведомления владельцу объявления
        pass



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
    def post(self, request, *args, **kwargs):
        response = get_object_or_404(Response, id=self.kwargs['pk'], announcement__author=request.user)
        response.accepted = True
        response.save()
        self.send_acceptance_notification(response)
        return redirect('user-responses')

    def send_acceptance_notification(self, response):
        # Логика отправки уведомления
        pass




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