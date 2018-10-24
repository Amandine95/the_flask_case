function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        //解决性别选择bug，判断单选框是否被选中来取值
        var gender = $('input:radio:checked').val()
        //遍历单选框
        // $('input:radio').each(function(){
        //     if(this.checked){
        //         gender = $(this).val()
        //     }
        // })

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        //  修改用户信息接口
        var params ={
            "signature":signature,
            "nick_name":nick_name,
            "gender":gender
        }
        $.ajax({
                url: "/user/base_info",
                type: "post",
                contentType: "application/json",
                headers: {
                "X-CSRFToken": getCookie("csrf_token")
                },
                data: JSON.stringify(params),
                success: function (resp) {
                    if (resp.errno == "0") {
                        // 更新父窗口内容
                        $('.user_center_name', parent.document).html(params['nick_name'])
                        $('#nick_name', parent.document).html(params['nick_name'])
                        $('.input_sub').blur()
                    }else {
                        alert(resp.errmsg)
                    }
                }




        })


    })
})