import uuid
from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView

from .forms import AddPostForm, UploadFileForm, ContactForm
from .models import Women, TagPost
from .utils import DataMixin


class WomenHome(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    title_page = 'Главная страница'
    cat_selected = 0

    def get_queryset(self):
        return Women.published.all().select_related('cat')

def handle_uploaded_file(f):
    name = f.name
    ext = ''
    date_file_name = datetime.now()
    if '.' in name:
        ext = name[name.rindex('.'):]
        name = name[:name.rindex('.')]

    suffix = str(uuid.uuid4())
    with open(f"uploads/{name}_{suffix}_{date_file_name}{ext}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required
def about(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['file'])
    else:
        form = UploadFileForm()

    return render(request, 'women/about.html', {'title': 'О сайте', 'form': form})


class ShowPost(DataMixin, DetailView):
    template_name = 'women/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['post'])

    def get_object(self, queryset=None):
        return get_object_or_404(Women.published, slug=self.kwargs[self.slug_url_kwarg])


class AddPage(PermissionRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'women/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Добавление статьи'
    permission_required = 'women.add_women'

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)


class UpdatePage(PermissionRequiredMixin, UpdateView):
    model = Women
    fields = ['title', 'content', 'photo', 'is_published', 'cat']
    template_name = 'women/addpage.html'
    title_page = 'Редактирование статьи'
    success_url = reverse_lazy('home')
    permission_required = 'women.change_women'


class ContactFormView(LoginRequiredMixin, DataMixin, FormView):
    form_class = ContactForm
    template_name = 'women/contact.html'
    success_url = reverse_lazy('home')
    title_page = "Обратная связь"

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


def login(request):
    return HttpResponse("Авторизация")


class WomenCategory(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Women.published.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        return self.get_mixin_context(context,
                                      title='Категория - ' + cat.name,
                                      cat_selected=cat.pk,
                                      )


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


class TagPostList(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег - ' + tag.tag)

    def get_queryset(self):
        return Women.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat')


