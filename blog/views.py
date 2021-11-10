from django.shortcuts import render, get_object_or_404
from .models import Post,Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm
from django.core.mail import message, send_mail

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by= 2
    template_name = 'blog/post/list.html'




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
                             
    return render(request, 'blog/post/detail.html', {'post': post})

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

