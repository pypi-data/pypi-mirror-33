# -*- coding:utf-8 -*-
from django.forms import model_to_dict


def article_to_dict(article):
    result = model_to_dict(article)
    result['created_time'] = article.created_time
    result['modified_time'] = article.modified_time
    result['summary'] = article.summary
    result['image'] = article.image
    return result


def article_to_preview_dict(article):
    return {'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'image': article.image,
            'created_time': article.created_time,
            'modified_time': article.modified_time
            }


def detail_category_dict(category):
    return {
        'category': model_to_dict(category),
        'category_meta': {
            'article_num': category.get_article_category_list().count()
        }
    }


def detail_tag_dict(tag):
    return {
        'tag': model_to_dict(tag),
        'tag_meta': {
            'article_num': tag.get_article_tag_list().count()
        }
    }


def category_tree_to_dict(category_tree):
    for c in category_tree:
        c.update(detail_category_dict(c['category']))
        if 'children':
            if c['children']:
                c['children'] = category_tree_to_dict(c['children'])
            else:
                c.pop('children')

    return category_tree


def comment_to_dict(comment):
    result = {
        'nickname': comment.nickname,
        'email': comment.email,
        'content': comment.content,
        'created_time': comment.created_time,
        'modified_time': comment.modified_time,
    }
    return result


def comment_list_to_dict(comment_list):
    for c in comment_list:
        c['comment'] = model_to_dict(c['comment'])
        if 'children' in c:
            if c['children']:
                c['children'] = comment_list_to_dict(c['children'])
            else:
                c.pop('children')
    return comment_list


def flatpage_to_dict(flatpage):
    result = model_to_dict(flatpage)
    result['created_time'] = flatpage.created_time
    result['modified_time'] = flatpage.modified_time
    return result
