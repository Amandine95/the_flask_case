from flask import render_template

from info.moudles.news import news_blu


@news_blu.route('/<int:news_id>')
def news_detail(news_id):
    """
    获取新闻详情
    """
    pass
    return render_template("news/detail.html")
