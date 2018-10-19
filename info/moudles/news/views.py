from flask import render_template

from info.moudles.news import news_blu


@news_blu.route('/<int:news_id>')
def news_detail(news_id):
    """
    获取新闻详情
    """
    # 传递data，详情页继承于base页面，base中需要用到data变量所以传入data
    data = {

    }
    return render_template("news/detail.html", data=data)
