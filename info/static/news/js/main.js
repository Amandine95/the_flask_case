$(function () {

    // 打开登录框
    $('.login_btn').click(function () {
        $('.login_form_con').show();
    })

    // 点击关闭按钮关闭登录框或者注册框
    $('.shutoff').click(function () {
        $(this).closest('form').hide();
    })

    // 隐藏错误
    $(".login_form #mobile").focus(function () {
        $("#login-mobile-err").hide();
    });
    $(".login_form #password").focus(function () {
        $("#login-password-err").hide();
    });

    $(".register_form #mobile").focus(function () {
        $("#register-mobile-err").hide();
    });
    $(".register_form #imagecode").focus(function () {
        $("#register-image-code-err").hide();
    });
    $(".register_form #smscode").focus(function () {
        $("#register-sms-code-err").hide();
    });
    $(".register_form #password").focus(function () {
        $("#register-password-err").hide();
    });


    // 点击输入框，提示文字上移
    $('.form_group').on('click focusin', function () {
        $(this).children('.input_tip').animate({
            'top': -5,
            'font-size': 12
        }, 'fast').siblings('input').focus().parent().addClass('hotline');
    })

    // 输入框失去焦点，如果输入框为空，则提示文字下移
    $('.form_group input').on('blur focusout', function () {
        $(this).parent().removeClass('hotline');
        var val = $(this).val();
        if (val == '') {
            $(this).siblings('.input_tip').animate({'top': 22, 'font-size': 14}, 'fast');
        }
    })


    // 打开注册框
    $('.register_btn').click(function () {
        $('.register_form_con').show();
        generateImageCode()
    })


    // 登录框和注册框切换
    $('.to_register').click(function () {
        $('.login_form_con').hide();
        $('.register_form_con').show();
        generateImageCode()
    })

    // 登录框和注册框切换
    $('.to_login').click(function () {
        $('.login_form_con').show();
        $('.register_form_con').hide();
    })

    // 根据地址栏的hash值来显示用户中心对应的菜单
    var sHash = window.location.hash;
    if (sHash != '') {
        var sId = sHash.substring(1);
        var oNow = $('.' + sId);
        var iNowIndex = oNow.index();
        $('.option_list li').eq(iNowIndex).addClass('active').siblings().removeClass('active');
        oNow.show().siblings().hide();
    }

    // 用户中心菜单切换
    var $li = $('.option_list li');
    var $frame = $('#main_frame');

    $li.click(function () {
        if ($(this).index() == 5) {
            $('#main_frame').css({'height': 900});
        }
        else {
            $('#main_frame').css({'height': 660});
        }
        $(this).addClass('active').siblings().removeClass('active');
        $(this).find('a')[0].click()
    })

    // 登录表单提交
    $(".login_form_con").submit(function (e) {
        e.preventDefault()
        var mobile = $(".login_form #mobile").val()
        var password = $(".login_form #password").val()

        if (!mobile) {
            $("#login-mobile-err").show();
            return;
        }

        if (!password) {
            $("#login-password-err").show();
            return;
        }

        // 发起登录请求
        var params = {
            "mobile":mobile,
            "password":password
        }
        $.ajax({
            url:'/passport/login',
            type:'post',
            headers:{
            "X-CSRFToken":getCookie('csrf_token')
            },
            contentType:'application/json',
            data: JSON.stringify(params),
            success:function(response){
                if(response.errno=='0'){
                    location.reload()


                }else{
                    alert(response.errmsg)
                     $("#register-password-err").html(response.errmsg);
                     $("#register-password-err").show();

                }

        }


        })
    })


    // 注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认提交操作,用ajax实现功能,局部刷新能够控制。form表单提交脱离控制
        e.preventDefault()

        // 取到用户输入的内容
        var mobile = $("#register_mobile").val()
        var smscode = $("#smscode").val()
        var password = $("#register_password").val()

        if (!mobile) {
            $("#register-mobile-err").show();
            return;
        }
        if (!smscode) {
            $("#register-sms-code-err").show();
            return;
        }
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }

        if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }
        // 准备参数,json格式对象
        var params = {
            "mobile":mobile,
            "smscode":smscode,
            "password":password

        }

        // 发起注册请求
        $.ajax({
            url:"/passport/register",
            type:"post",
            data:JSON.stringify(params),
            //在headers添加csrf_token随机值
            headers:{
            "X-CSRFToken":getCookie('csrf_token')
            },
            contentType:"application/json",
            success:function(response){
                if(response.errno=="0"){
                //    注册成功，代表登陆成功,定位到当前页面
                    location.reload()

                }else{
                //    注册失败
                    alert(response.errmsg)
                    $("#register-password-err").html(response.errmsg);
                    $("#register-password-err").show();


                }

            }
        })

    })
})

var imageCodeId = ""

// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
//    浏览器发起图片验证码请求/image_code?imageCodeId=xxx(浏览器端通过UUID生成唯一图片验证码，请求时携带)
    imageCodeId = generateUUID()
//    生成url
    var url = '/passport/image_code?imageCodeId=' + imageCodeId
//    给指定img标签设置src(给标签设置属性),设置之后img标签就会向这个地址发请求，请求图片(后端由视图函数接收这个请求并返回图片)
    $(".get_pic_code").attr("src", url)


}

// 发送短信验证码
function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    // 点击发送按钮后暂时移除点击事件
    $(".get_code").removeAttr("onclick");
    var mobile = $("#register_mobile").val();
    if (!mobile) {
        $("#register-mobile-err").html("请填写正确的手机号！");
        $("#register-mobile-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err").html("请填写验证码！");
        $("#image-code-err").show();
        // 设回点击事件
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }

    // 发送短信验证码
//    ajax代码，将填好的手机号、图码内容作为参数传给后端验证，局部刷新
    var params = {
        "mobile": mobile,
        "image_code": imageCode,
        "image_code_id": imageCodeId

    }
//    发起注册请求
    $.ajax({
        //请求地址
        url: "/passport/sms_code",
        //请求方式
        type: "post",
        //在headers添加csrf_token随机值
        headers:{
            "X-CSRFToken":getCookie('csrf_token')
        },
        //请求参数,json对象转为json格式的字符串
        data: JSON.stringify(params),
        //请求参数数据类型
        contentType: "application/json",
        //请求发送后的处理(后端传递验证码的发送结果过来)
        success: function (response) {
            if (response.errno == "0") {
            //    发送成功

            //进入倒计时
                var num = 60
                //设置延时器
                var t = setInterval(function() {
                    if (num == 1) {
                        // 倒计时结束、a标签显示内容、重新设置点击事件
                        $('.get_code').html("点击获取验证码");
                        $(".get_code").attr("onclick", "sendSMSCode();");
                        // 清除倒计时
                        clearInterval(t)


                    } else {
                        num -= 1
                        // a标签显示的内容，即倒计时时间
                        $('.get_code').html(num + "秒");
                    }

                },1000)

            }else{
            //发送失败
                alert(response.errmsg)
                $(".get_code").attr("onclick", "sendSMSCode();")



            }

        }

    })


}
function logout() {
    //$.get() 是get请求方式的ajax的简写  $.post()
    $.get('/passport/logout',function(response){
        //刷新当前页面
        location.reload()

    })
    
}

// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        $li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num) {
    var $frame = $('#main_frame');
    $frame.css({'height': num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}
