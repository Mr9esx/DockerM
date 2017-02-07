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
        $.ajax({
            url: "/control/container/start_container",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id, "container_name": container_name },    //参数值
            type: "POST",   //请求方式
            success: function(req) {
                createPNotify(req['title'],req['text'],req['status']);
            },error: function (req) {
                createPNotify('操作发送失败！', '请检查网络连通性！', 'error');
            }
        });
    });

    $('.stopbtn').click(function () {
        container_id = $(this).attr('value');
        container_name = $(this).data('name');
        $.ajax({
            url: "/control/container/stop_container",    //请求的url地址
            dataType: "json",   //返回格式为json
            async: true, //请求是否异步，默认为异步，这也是ajax重要特性
            data: { "container_id": container_id, "container_name": container_name },    //参数值
            type: "POST",   //请求方式
            success: function(req) {
                createPNotify(req['title'],req['text'],req['status']);
            },error: function (req) {
                createPNotify('操作发送失败！', '请检查网络连通性！', 'error');
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
                createPNotify(req['title'],req['text'],req['status']);
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
                createPNotify(req['title'],req['text'],req['status']);
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
                createPNotify(req['title'],req['text'],req['status']);
            },error: function (req) {
                createPNotify('操作发送失败！', '请检查网络连通性！', 'error');
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
                createPNotify(req['title'],req['text'],req['status']);
            }
            ,error: function (req) {
                createPNotify('操作发送失败！', '请检查网络连通性！', 'error');
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
                createPNotify(req['title'],req['text'],req['status']);
            }
            ,error: function (req) {
                createPNotify('操作发送失败！', '请检查网络连通性！', 'error');
            }
        });
    });

    $('.refreshbtn').click(function () {
        alert('ok');
    });

    $('#addHost_btn').click(function (){
        //获取容器名称
        var container_name = $('#saltstack_id').val();

        //获取主机名
        var hostname = $('#hostname').val();

        var command = new Array();
        var link_list = new Array();
        var port_list = new Array();
        var saltstack_id = null;
        var image_name = null;
        var image_id = null;

        //获取主机
        try {
            saltstack_id = $('#host_list_select').select2("data")[0].text;
        }
        catch(err) {
            showError($("#addHost_btn"), $("#create_error"), 'container_ischoose', '请选择主机！');
            return false;
        }

        //获取镜像
        try {
            image_name = $('#image_list_select').select2("data")[0].text;
            image_id = $('#image_list_select').select2("data")[0].id;
        }
        catch(err) {
             showError($("#addHost_btn"), $("#create_error"), 'image_ischoose', '请选择镜像！');
            return false;
        }

        //获取命令
        var data = $("#command").tagsInput('items');
        $.each(data,function(i,e){
            command = e.value;
        });

        //获取链接
        $("#link_list").children('.tag').each(function() {
            var tmp = "{\""+$(this).children('span').data('container-name')+"\" : \""+$(this).children('span').data('alias')+"\"}";
            link_list.push(tmp);
        });

        //获取端口
        $("#port_list").children('.tag').each(function() {
            var tmp = "{"+"\"container-port\" : \""+($(this).children('span').data('container-prot'))+"\",\"protocol\" : \""+($(this).children('span').data('protocol'))+"\",\"host-addredd\" : \""+($(this).children('span').data('host-addredd'))+"\",\"host-port\" : \""+($(this).children('span').data('host-port'))+"\"}";
            port_list.push(tmp);
        });
        // console.log(port_list);
        // console.log(link_list);
        $.ajax({
            url: "/control/container/create",
            dataType: "json",
            async: true,
            data: {
                "saltstack_id": saltstack_id,
                "container_name": container_name,
                "image_name": image_name,
                "image_id": image_id,
                "hostname": hostname,
                "command": command,
                "link": link_list,
                "port": port_list
            },
            type: "POST",
            success: function (req) {
                createPNotify(req['title'],req['text'],req['status']);
            }
            , error: function (req) {
                createPNotify('操作发送失败！', '请检查网络连通性！', 'error');
            }
        });
    });

    function createPNotify(title,text,type){
        new PNotify({
            title: title,
            text: text,
            type: type,
            styling: 'bootstrap3',
            addclass: "stack_bar_top",
            stack: stack_bar_top
        });
    }
});