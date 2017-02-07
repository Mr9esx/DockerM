var Tools = {
    unique : function(){

    }
}

function checkHostIsAlive(saltstack_list){
    for(var i =0 ; i < saltstack_list.length;i++){
        saltstack_id = saltstack_list[i]
        $.ajax({
            url: "/api/hostIsAlive/",
            dataType: "json",
            async: false,
            data: {
                "saltstack_id": saltstack_id
            },
            type: "POST",
            success: function (req) {
                console.log(req);
                if (req.status === true){
                    $("."+saltstack_id).attr('class',saltstack_id+' fa fa-check fa-fw icon-success');
                }else{
                    $("."+saltstack_id).attr('class',saltstack_id+' fa fa-times fa-fw icon-error');
                }
            }
            , error: function (req) {
                console.log(req);
            }
        });
    }
}
