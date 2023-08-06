DeerU Api
==========

DeerU接口扩展，返回json数据

目录
=====

    * `安装`_
    
    * `数据格式`_
    
        - `基础格式`_

        - `其他数据格式`_

            + `Article <article-json_>`_
            + `ArticleMeta <article-meta-json_>`_
            + `Category <category-json_>`_
            + `CategoryMeta <category-meta-json_>`_
            + `Tag <tag-json_>`_
            + `TagMeta <tag-meta-json_>`_
            + `Comment <comment-json_>`_

    * `接口`_

        - `获取config`_
        - `获取文章`_
        - `获取文章列表`_
        - `获取分类`_
        - `获取分类列表`_
        - `获取分类树`_
        - `获取标签`_
        - `获取标签列表`_
        - `创建评论`_
        - `获取文章的评论列表`_


安装
========

    1. 使用pip安装:: 

        pip install deeru-api

    2. 把app添加到 ``deeru/settings_local.py`` 中:: 

        CUSTOM_APPS = [
            'deeru_api.apps.DeerUApiConfig'
        ]

    3. 在 ``urls_local.py`` 中自定义你的接口url:: 

        urlpatterns = [
            path('api/', include('deer_api.urls')),
        ]

数据格式
=========

基础格式
--------
    接口返回的数据必带有一个 ``code`` ，``code`` 为0表示正常，不为0会有一个 ``msg`` 为错误提示，

    基本格式如下:: 

        {
            'code' : 0,
            'msg'  : 'xx',

            # 其他数据
            ...
        }

其他数据格式
------------
    接口为Article、Category等设计了一个通用数据格式，接口中返回的每种类型的数据格式都是一样的。

    .. _article-json:

    * Article:: 

        {
            'id': 12,
            'content': 'xxx', # 正文
            'image': 'http://xx', # 封面图片
            'summary': 'xxx', # 简介
            'title': 'title',
            'created_time': '2018-03-12T11:23:00',
            'modified_time': '2018-03-12T11:23:00',
        }

    .. _article-meta-json:

    * ArticleMeta:: 

        {
            'id': 12, # 注意，这个是article_meta的id
            'article_id': 12
            'comment_num': 3
            'read_num': 333
        }

    .. _category-json:

    * Category:: 

        {
            'id': 1,
            'name': 'xxx', 
            'father_id': -1, # 父类别id，-1表示无父类别
            'm_order': 4, # 用于排序
            
        }

    .. _category-meta-json:

    * CategoryMeta:: 

        {
            'article_num': 10,
            
        }

    .. _tag-json:

    * Tag:: 

        {
            'id': 12,
            'name': 'xxx',
        }

    .. _tag-meta-json:

    * TagMeta:: 

        {
            'article_num': 10,
            
        }
    
    .. _comment-json:

    * Comment:: 

        {
            # 下面所说的评论和回复其实是一个东西，两个名字只是为了方便区别
            
            # 评论 -- 对文章的评论叫评论
            # 回复 -- 对评论的回复叫回复 ，对回复的回复也叫回复

            'id': 1,
            'content': 'xxx',
            'email': '123@123.com',
            'nickname': 'xx',
            'article_id': 12, # 哪个文章下的评论
            'type': 201 , # 201: 评论 ；202: 回复

            # 关于 root_id, to_id具体解释可查看DeerU源码中 app.app_models.content_model.Comment 下的注释，里面有详细说明

            'to_id': -1, # 回复的评论id。对文章评论时，这一项无意义。
            'root_id': -1, # 根评论id。对文章评论时，这一项无意义；对评论回复时就是评论的id，对回复回复时，是最早的那条评论id
        }


接口
--------

获取config
````````````
获取配置中设置为到context的所有配置

* url ： ``app_config``

* 请求方法 ： ``GET``

* 参数 ： 

* 返回值:: 

    {
        'code':0,
        'config':{
            'global_value':{ ... },
            'top_ico':{ ... },
            'top_menu':{ ... },
            'common_config':{ ... },
            
            ...
        }
    }
    
获取文章
````````````

* url ： ``article/<int:article_id>``

* 请求方法 ： ``GET``

* 参数 ： 

* 返回值:: 

    {
        'code':0,
        'article': Article , # Article类型，结构参照上面
        'article_meta': ArticleMeta ,
        'category': [ Category, Category ],
        'last_article': Article,
        'next_article': Article,
        'tags': [ Tag, Tag ],

    }


获取文章列表
````````````

* url ： ``article_list``

* 请求方法 ： ``GET``

* 参数 ： 
    
    - page : 页数，默认：1

    - pre_page : 一页多少文章，默认：7

    - filter_type : 筛选类型，可选项如下：

        + article : 默认，筛选所有文章

        + category : 筛选分类下文章

        + tag : 筛选标签下文章

    - category_id : 筛选分类下文章时指定分类id

    - tag_id : 筛选标签下文章时指定标签id


* 返回值:: 

    {
        'code':0,
        'article_list': [
                {
                    'article': Article , 
                    'article_meta': ArticleMeta ,
                    'category': [ Category, Category ],
                    'tags': [ Tag, Tag ],
                },

                { ... }
         ],

        'paginator': {
                'end_index': 4 , # 最大页码 
                'current_page_num': 1 ,# 当前页码
        }

    }


获取分类
````````````

* url ： ``category/<int:category_id>``

* 请求方法 ： ``GET``

* 参数 ： 

* 返回值:: 

    {
        'code':0,
        'category': Category,
        'category_meta': CategoryMeta,

    }

获取分类列表
````````````

* url ： ``category_list``

* 请求方法 ： ``GET``

* 参数 ： 

* 返回值:: 

    {
        'code':0,
        'category_list': [ 

                {
                    'category': Category,
                    'category_meta': CategoryMeta
                },

                {...} 
        ]

    }

获取分类树
````````````
返回按父子结构整理后的分类list

* url ： ``category_tree``

* 请求方法 ： ``GET``

* 参数 ： 

* 返回值:: 

    {
        'code':0,
        'category_tree': [ 

                {
                    'category': Category,
                    'category_meta': CategoryMeta
                    'children':[
                        
                        {
                            'category': Category,
                            'category_meta': CategoryMeta
                            'children':[ ... ]
                        },
                    ]
                },

                {...} 
        ]

    }

获取标签
````````````

* url ： ``tag/<int:tag_id>``

* 请求方法 ： ``GET``

* 参数 ： 

* 返回值:: 

    {
        'code':0,
        'tag': Tag,
        'tag_meta': TagMeta,

    }

获取标签列表
````````````

* url ： ``tag_list``

* 请求方法 ： ``GET``

* 参数 ： 

* 返回值:: 

    {
        'code':0,
        'tag_list': [ 

                {
                    'tag': Tag,
                    'tag_meta': TagMeta,
                },

                {...} 
        ]

    }

创建评论
````````````
创建评论，需要注意 ``POST`` 请求需要在 cookies 里添加 csrftoken

* url ： ``comment/create``

* 请求方法 ： ``POST``

* 参数 ： 

    - content : 内容

    - email : 可不填

    - nickname : nickname

    - type : type，可选项如下：
    
        + 201 : 对文章评论

        + 202 : 对评论评论

    - to_id : 回复的评论id，具体说明参见 `Comment <comment-json_>`_ 结构说明，以及DeerU源码
    
    - root_id : 根评论id，具体说明参见 `Comment <comment-json_>`_ 结构说明，以及DeerU源码


* 返回值:: 

    {
        'code':0
    }

获取文章的评论列表
``````````````````

返回父子结构的评论list

* url ： ``comment_list``

* 请求方法 ： ``GET``

* 参数 ： 

    - article_id : 文章id

* 返回值:: 

    {
        # 注意：children里不会再有children

        'code':0,
        'comment_list': [ 

                {
                    'comment': Comment,
                    'children': [ 
                            {
                                'comment': Comment,
                                'to_nickname': 'xx'
                            }, 
                            
                            { ... } 
                    ],
                },

                {...} 
        ]

    }
