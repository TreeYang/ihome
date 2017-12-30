function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $.get('/api/v1/user/', function(data){
        $('#user-avatar').attr('src',data.user.avatar_url);
        $('#user-name').val(data.user.name);
    })
})

$('#form-avatar').submit(function(){
    $('#error-msg1').hide();
    $(this).ajaxSubmit({
        url:"/api/v1/user/",
        type:"put",
        dataType:"json",
        success:function(data){
            console.log(data);
            if(data.code==RET.OK){
                $('#user-avatar').attr('src', data.user.url)
            }else{
                $('#error-msg1').show();
            }
        }
    });
    return false
});

$('#form-name').submit(function(){
    $('#error-msg2').hide();
    $(this).ajaxSubmit({
        url:"/api/v1/user/",
        type:"put",
        dataType:{'name':$('#user-name').val()},
        success:function(data){
            if(data.code==RET.OK){
                //
            }else{
                $('#error-msg2').show();
            }

        }
    });
    return false
});

