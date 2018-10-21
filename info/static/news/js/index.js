var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据(加载标志)

//页面加载完后就调用这个回调函数
$(function () {
    //页面加载完后加载新闻数据
    updateNewsData()
    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid')
        //遍历所有li，去除选中效果
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        //当前li添加选中效果
        $(this).addClass('active')

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid

            // 重置分页参数
            cur_page = 1
            total_page = 1
            updateNewsData()
        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // 判断页数，去更新新闻数据
        //    如果没有正在向后台请求数据，就加载数据
            if(!data_querying){
                data_querying=true
                //当前页数小于总页数，则加载
                if (cur_page<total_page){
                     //    当前页数加1
                    cur_page+=1
                //    加载数据
                    updateNewsData()

                }


            }

        }
    })
})

function updateNewsData() {
    // 更新新闻数据
    var params={
        "cid":currentCid,
        "page":cur_page
    }
    //ajax 的 get 请求简写      function是请求完成后的回调函数
    $.get('/news_list',params,function(response){
        //请求成功后，数据加载完毕，将加载标志改为false，表示当前没有在请求数据
        data_querying=false
        if (response.errno=="0"){
        //    总页数
            total_page=response.data.total_page

        //    请求成功:1、当前页面为 1 时清除html已有数据(js操作)
            if(cur_page==1){
                $(".list_con").html("")

            }

        //    2、添加请求返回的数据
             for (var i=0;i<response.data.news_dict_list.length;i++) {
                var news = response.data.news_dict_list[i]
                var content = '<li>'
                // 添加详情页跳转功能,href属性添加请求路径(新闻详情的路由)
                content += '<a href="/news/'+news.id+'" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>'
                content += '<a href="/news/'+news.id+'" class="news_title fl">' + news.title + '</a>'
                content += '<a href="/news/'+news.id+'" class="news_detail fl">' + news.digest + '</a>'
                content += '<div class="author_info fl">'
                content += '<div class="source fl">来源：' + news.source + '</div>'
                content += '<div class="time fl">' + news.create_time + '</div>'
                content += '</div>'
                content += '</li>'
                $(".list_con").append(content)
            }


        }else{
        //    请求失败
            alert(response.errmsg)

        }
    })
}
