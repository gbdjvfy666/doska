from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse, reverse_lazy
from .form import AnnouncementForm, ResponseForm, AdForm
from .models import Announcement, Response, Ad
from .utils import send_notification_email
from django.views.generic import ListView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail

User = get_user_model()

def send_response_notification_email(response):
    subject = 'Уведомление о новом отклике на ваше объявление'
    message = 'У вас новый отклик на объявление. Проверьте ваш профиль для получения подробностей.'
    html_message = render_to_string('response_email.html', {'response': response})
    recipient_list = [response.ad.author.email]
    send_mail(subject, message, None, recipient_list, html_message=html_message)

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
        return reverse_lazy('announcement-detail', kwargs={'pk': self.object.pk})

class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcements/list.html'
    context_object_name = 'announcements'

class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'announcements/detail.html'
    context_object_name = 'announcement'

class ResponseCreateView(LoginRequiredMixin, CreateView):
    model = Response
    form_class = ResponseForm
    template_name = 'responses/create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.announcement = get_object_or_404(Announcement, pk=self.kwargs['announcement_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('announcement-detail', kwargs={'pk': self.kwargs['announcement_id']})
    

class ResponseDeleteView(LoginRequiredMixin, DeleteView):
    model = Response
    success_url = reverse_lazy('user-responses')

    def get_queryset(self):
        return Response.objects.filter(announcement__author=self.request.user)


def send_notification(user, message):
    send_mail(
        'Notification',
        message,
        'noreply@example.com',
        [user.email],
        fail_silently=False,
    )

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
    
def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    responses = ad.responses.all()
    return render(request, 'ad_detail.html', {'ad': ad, 'responses': responses})

@login_required
def response_list(request):
    responses = Response.objects.filter(user=request.user)
    return render(request, 'responses/response_list.html', {'responses': responses})

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
def delete_response(request, response_pk):
    response = get_object_or_404(Response, pk=response_pk)
    if response.announcement.author != request.user:
        return redirect('announcement-list')
    response.delete()
    messages.success(request, 'Отклик удален.')
    return redirect('responses_by_announcement', announcement_pk=response.announcement.pk)

@login_required
def accept_response(request, response_pk):
    response = get_object_or_404(Response, pk=response_pk)
    if response.announcement.author != request.user:
        return redirect('announcement-list')
    response.is_accepted = True
    response.save()
    send_notification_email(response.user.email, response.announcement.title)
    messages.success(request, 'Отклик принят.')
    return redirect('responses_by_announcement', announcement_pk=response.announcement.pk)