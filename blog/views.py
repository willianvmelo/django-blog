from django.shortcuts import render, get_object_or_404
from .models import Post,Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm
from django.core.mail import message, send_mail
from taggit.models import Tag


def post_list(request,tag_slug = None):
    
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag,slug = tag_slug)
        object_list = object_list.filter(tags__in = [tag])

    paginator = Paginator(object_list, 4)  # 4 posts por página
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro entrega a primeira página
        posts = paginator.page(1)
    except EmptyPage:
        # Se a página estiver vazia entrega a última página
        posts = paginator.page(paginator.num_pages)

    return render(request,
                'blog/post/list.html',
                {'page': page,
                'posts': posts,
                'tag' : tag})



def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month, publish__day=day)

    # Obtendo a lista dos comentários ativos
    comments = post.comments.filter(active = True) 
    new_comment = None

    if request.method == 'POST' :
        # Um comentário foi postado
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():

            # Cria o objeto Comment mas não o salva ainda no banco de dados.j

            new_comment = comment_form.save(commit=False)

            # Atribui a postagem atual ao comentário

            new_comment.post = post

            # salva o comentário no banco de dados

            new_comment.save()
    else:
        comment_form = CommentForm()

        return render(request,
        'blog/post/detail.html',
        {
        'post' : post,
        'comments' : comments,
        'new_comment' : new_comment,
        'comment_form' : comment_form

        })        
                             
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form})

# View para compartilhamento de posts via email

def post_share(request,post_id):
    # obtém a postagem com base no id
    post = get_object_or_404(Post,id=post_id,status='published')
    sent = False
    if request.method == 'POST':
        # Formulário submetido
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Os campos do formulário passaram pela validação
            cd = form.cleaned_data
            # ... envia o email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url} \n \n \
                {cd['name']}' comments: {cd['comments']}"
            send_mail(subject,message,'admin@email.com',[cd['to']])    
            sent = True
    else:
        form = EmailPostForm()
    return render(request,'blog/post/share.html',{
        'form':form,
        'post':post,
        'sent':sent
    })             

