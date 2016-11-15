$(document).ready(function(){
    function getRootPath() {
        var pathName = window.location.pathname.substring(1);
        var webName = pathName == '' ? '' : pathName.substring(0, pathName.indexOf('/'));
        return window.location.protocol + '//' + window.location.host + '/'+ webName;
    }
    var stack_bar_top = {"dir1": "up", "dir2": "left", "push": "top", "spacing1": 0, "spacing2": 15};
    $('.startbtn').click(function () {
        container_id = $(this).attr('value');
        container_name = $(this).attr('data-name');
        $(this).children('span').text('容器启动中...');
        $.ajax({
            url: "/control/container/start",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id },    //参数值
            type: "POST",   //请求方式
            success: function(req) {
                new PNotify({
                    title: '操作发送成功！',
                    text: '启动容器 '+ container_name + ' [' + container_id.substring(0,12)+ ']',
                    type: 'success',
                    styling: 'bootstrap3',
                    addclass: "stack_bar_top",
                    stack: stack_bar_top
                });
            }
            ,error: function (req) {
                new PNotify({
                    title: '操作发送失败！',
                    text: '请检查网络连通性！',
                    type: 'error',
                    styling: 'bootstrap3',
                    addclass: "stack_bar_top",
                    stack: stack_bar_top
                });
            }
        });
    });

    $('.stopbtn').click(function () {
        container_id = $(this).attr('value');
        shortID = container_id.substring(0,12)
        $(this).children('span').text('容器关闭中...');
        $.ajax({
            url: "/control/container/stop",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id },    //参数值
            type: "POST",   //请求方式
            success: function(req) {
                alert("ok");
            },error: function (req) {
                alert("no");
            }
        });
    });

    $('.unpausebtn').click(function () {
        container_id = $(this).attr('value');
        shortID = container_id.substring(0,12)
        $(this).children('span').text('容器恢复中...');
        $.ajax({
            url: "/container/control/unpause",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id },    //参数值
            type: "POST",   //请求方式
            success: function(req) {

            },error: function (req) {

            }
        });
    });

    $('.pausebtn').click(function () {
        container_id = $(this).attr('value');
        shortID = container_id.substring(0,12)
        $(this).children('span').text('容器暂停中...');
        $.ajax({
            url: "/container/control/pause",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id },    //参数值
            type: "POST",   //请求方式
            success: function(req) {

            },error: function (req) {

            }
        });
    });

    $('.deletebtn').click(function () {
        container_id = $(this).attr('value');
        shortID = container_id.substring(0,12)
        $(this).children('span').text('容器删除中...');
        $.ajax({
            url: "/container/control/delete",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id },    //参数值
            type: "POST",   //请求方式
            success: function(req) {

            },error: function (req) {

            }
        });
    });

    $('.followbtn').click(function () {
        container_id = $(this).attr('value');
        container_name = $(this).attr('data-name');
        $.ajax({
            url: "/control/container/follow",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id },    //参数值
            type: "POST",   //请求方式
            success: function(req) {
                new PNotify({
                    title: '操作发送成功！',
                    text: '关注容器 '+ container_name + ' [' + container_id.substring(0,12)+ ']',
                    type: 'success',
                    styling: 'bootstrap3',
                    addclass: "stack_bar_top",
                    stack: stack_bar_top
                });
            }
            ,error: function (req) {
                new PNotify({
                    title: '操作发送失败！',
                    text: '请检查网络连通性！',
                    type: 'error',
                    styling: 'bootstrap3',
                    addclass: "stack_bar_top",
                    stack: stack_bar_top
                });
            }
        });
    });

    $('.unfollowbtn').click(function () {
        container_id = $(this).attr('value');
        container_name = $(this).attr('data-name');
        $.ajax({
            url: "/control/container/unfollow",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id },    //参数值
            type: "POST",   //请求方式
            success: function(req) {
                new PNotify({
                    title: '操作发送成功！',
                    text: '取消关注容器 '+ container_name + ' [' + container_id.substring(0,12)+ ']',
                    type: 'success',
                    styling: 'bootstrap3',
                    addclass: "stack_bar_top",
                    stack: stack_bar_top
                });
            }
            ,error: function (req) {
                new PNotify({
                    title: '操作发送失败！',
                    text: '请检查网络连通性！',
                    type: 'error',
                    styling: 'bootstrap3',
                    addclass: "stack_bar_top",
                    stack: stack_bar_top
                });
            }
        });
    });

    $('.refreshbtn').click(function () {
        alert('ok');
    });
});