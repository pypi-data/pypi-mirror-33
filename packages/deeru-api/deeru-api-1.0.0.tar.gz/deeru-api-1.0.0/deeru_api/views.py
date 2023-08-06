from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict

from app.app_models.content_model import Article
from app.db_manager.content_manager import get_article_meta_by_article, get_article_by_id, filter_article_order_by_id, \
    filter_article_by_category, filter_article_by_tag, get_category_by_id, get_tag_by_id, get_all_category, get_all_tag

from app.ex_paginator import DeerUPaginator
from app.forms import CommentForm
from app.manager import get_config_context
from app.manager.ct_manager import get_category_tree2
from deeru_api.manager import article_to_dict, comment_to_dict, article_to_preview_dict, detail_category_dict, \
    detail_tag_dict, category_tree_to_dict, comment_list_to_dict
from deeru_api.response import JsonSuccessResponse, JsonFailResponse


def app_config_view(request):
    result = {'config': get_config_context()}
    return JsonSuccessResponse(result)


def detail_article_view(request, article_id):
    try:
        article_meta = get_article_meta_by_article(article_id)
        article_meta.read_num += 1
        article_meta.save()
    except:
        return JsonFailResponse({'code': 404, 'msg': 'article_id不存在'})

    article = get_article_by_id(article_id)

    result = {
        'article': article_to_dict(article),
        'article_meta': model_to_dict(article_meta),
        'category': [model_to_dict(c) for c in article.category()],
        'tags': [model_to_dict(t) for t in article.tags()],
        'last_article': article.last_article(),
        'next_article': article.next_article()
    }

    return JsonSuccessResponse(result)


def article_list_view(request):
    filter_type = request.GET.get('filter_type', 'article')
    per_page = int(request.GET.get('per_page', 7))
    page = int(request.GET.get('page', 1))

    if page < 1:
        return JsonFailResponse({'msg': 'page无效'})

    result = {}

    if filter_type == 'article':
        paginator = DeerUPaginator(filter_article_order_by_id(), per_page, page)

    elif filter_type == 'category':
        category_id = request.GET.get('category_id')
        if not category_id:
            return JsonFailResponse({'msg': '缺少必要参数category_id'})
        paginator = DeerUPaginator(filter_article_by_category(category_id).order_by('-id'), per_page, page)

        # category = get_category_by_id(category_id)
        # result = detail_category_dict(category)

    elif filter_type == 'tag':
        tag_id = request.GET.get('tag_id')
        if not tag_id:
            return JsonFailResponse({'msg': '缺少必要参数tag_id'})
        paginator = DeerUPaginator(filter_article_by_tag(tag_id).order_by('-id'), per_page, page)

        # tag = get_tag_by_id(tag_id)
        # result = detail_tag_dict(tag)
    else:
        return JsonFailResponse({'msg': '参数filter_type错误'})

    if page > paginator.end_index:
        return JsonFailResponse({'msg': 'page无效'})

    article_list = paginator.page(page).object_list
    result['article_list'] = []
    result['paginator'] = {'end_index': paginator.end_index,
                           'current_page_num': page}

    for article in article_list:
        result['article_list'].append({'article': article_to_preview_dict(article),
                                       'article_meta': model_to_dict(article.meta_data()),
                                       'category': [model_to_dict(c) for c in article.category()],
                                       'tags': [model_to_dict(t) for t in article.tags()],
                                       })

    return JsonSuccessResponse(result)


def detail_category_view(request, category_id):
    category = get_category_by_id(category_id)

    return JsonSuccessResponse(detail_category_dict(category))


def category_list_view(request):
    categorys = get_all_category()
    result = {'category_list': []}
    for c in categorys:
        result['category_list'].append(detail_category_dict(c))

    return JsonSuccessResponse(result)


def category_tree_view(request):
    category_tree = get_category_tree2()

    return JsonSuccessResponse({'category_tree': category_tree_to_dict(category_tree)})


def detail_tag_view(request, tag_id):
    tag = get_tag_by_id(tag_id)

    return JsonSuccessResponse(detail_tag_dict(tag))


def tag_list_view(request):
    tags = get_all_tag()
    result = {'tag_list': []}
    for t in tags:
        result['tag_list'].append(detail_tag_dict(t))

    return JsonSuccessResponse(result)


def create_comment(request):
    if request.method == 'POST':

        form = CommentForm(request.POST)
        if form.is_valid():
            article_id = form.cleaned_data['article_id']
            article = get_article_by_id(article_id)

            if not article:
                return JsonFailResponse({'msg': 'article_id不存在'})
            form.save()

            return JsonSuccessResponse({})


def comment_list_view(request):
    article_id = request.GET.get('article_id')
    if not article_id:
        return JsonFailResponse({'msg': '缺少必要参数'})

    comment_list = Article(id=article_id).format_comments()

    result = {'comment_list': comment_list_to_dict(comment_list)}
    print(result)

    return JsonSuccessResponse(result)
