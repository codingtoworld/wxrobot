var send_to_users = new Array();
var send_last_user = null;
var ws = null;
var wx_check_count = 0;
var href = window.location.href.replace(/http/, "ws");
var ws_url = href.replace(/wechat/, "wsmessage");

var heartCheck = {
    timeout: 60000,//60ms
    timeoutObj: null,
    serverTimeoutObj: null,
    reset: function(){
        wx_check_count = 0;
        clearTimeout(this.timeoutObj);
        clearTimeout(this.serverTimeoutObj);
　　　　 this.start();
    },
    start: function(){
        var self = this;
        wx_check_count++;
        if (wx_check_count > 10){return false;}
        this.timeoutObj = setTimeout(function(){
            ws.send("6469616e6e616f3531");
            console.log("run client timeout");
            self.serverTimeoutObj = setTimeout(function(){
                console.log("run server timeout");
                ws.close();
            }, self.timeout)
        }, this.timeout)
    },
};

function blodurl(str,type="image/jpg"){
    var raw = atob(str);
    var rawLength = raw.length;
    var uInt8Array = new Uint8Array(rawLength);
    for (var i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
    }
    b = new Blob([uInt8Array], {type: type});
    return URL.createObjectURL(b);
}

var chat = {
    messageToSend: '',
    init: function() {
        this.cacheDOM();
        this.bindEvents();
        this.render();
    },
    cacheDOM: function() {
        this.$chatHistory = $('.chat-history');
        this.$button = $('#send-btn');
        this.$textarea = $('#message-to-send');
        this.$chatHistoryList =  this.$chatHistory.find('ul');
    },
    bindEvents: function() {
        this.$button.on('click', this.addMessage.bind(this));
        this.$textarea.on('keyup', this.addMessageEnter.bind(this));
    },

    wsRenderSelf:function(msg){
        var template = $("#message-template").html();
        var messageOutput = msg.content.data;
        if (msg.content.type==4){
            messageOutput = '<span id="au_'+msg.msg_id+'" data-voice="'+msg.content.voice+'" class="icon glyphicon glyphicon-volume-high" style="cursor:pointer">点击播放语音</span>';
        }
        if (msg.content.type==3){
            messageOutput = '<a id="lighter_'+msg.msg_id+'" href="javascript:void(0);">';
            messageOutput = messageOutput+ '<img id="img_'+msg.msg_id+'" src="data:image/png;base64,'+msg.content.img+'" data-action="zoom" style="cursor:pointer" width="168">';
            messageOutput = messageOutput + '</a>';
        }
        var context = {
            userId:msg.to_user.id.replace(/@/,''),
            toUser:(msg.to_user.name=='')?'unknow':msg.to_user.name,
            messageOutput: messageOutput,
            time: this.getCurrentTime(msg.msg_time*1000)
        };
        $.tmpl(template,context).find(".message-data").click(function(){
                $("#wechat-content ul li").hide();
                $(".U-"+context['userId']).show();
                elt.tagsinput('removeAll');
                elt.tagsinput('add', { "value": msg.to_user.id , "text": msg.to_user.name, "sex": 0 });
            }).end().appendTo(this.$chatHistoryList);
        if (msg.content.type==3){
            $('#lighter_'+msg.msg_id).click(function(){
                $(this).attr('href',$("#img_"+msg.msg_id).attr('src'));
                $(this).lighter();return false;
            });
        }
        if (msg.content.type==4){
            $("#au_"+msg.msg_id).click(function(){
                var audioElement = document.createElement('audio');
                audioElement.setAttribute('src',blodurl($(this).data("voice"),"audio/mpeg"));
                audioElement.play();
            });
        }

    },
    wsRenderFriend:function(msg){
        var templateResponse = $("#message-response-template").html();
        var response = msg.content.data;
        if (msg.content.type==4){
            response = '<span id="au_'+msg.msg_id+'" data-voice="'+msg.content.voice+'" class="icon glyphicon glyphicon-volume-high" style="cursor:pointer">点击播放语音</span>';
        }
        if (msg.content.type==3){
            response = '<a id="lighter_'+msg.msg_id+'" href="javascript:void(0);">';
            response = response+ '<img id="img_'+msg.msg_id+'" src="data:image/png;base64,'+msg.content.img+'" data-action="zoom" style="cursor:pointer" width="168">';
            response = response + '</a>';
        }
        var resContext = {
            userId:msg.from_user.id.replace(/@/,''),
            user: msg.from_user.name,
            response:response,
            time: this.getCurrentTime(msg.msg_time*1000)
        };
        $.tmpl(templateResponse,resContext).find(".message-data").click(function(){
                $("#wechat-content ul li").hide();
                $(".U-"+resContext['userId']).show();
                elt.tagsinput('removeAll');
                elt.tagsinput('add', { "value": msg.from_user.id , "text": msg.from_user.name, "sex": 0 });
            }).end().appendTo(this.$chatHistoryList);
        if (msg.content.type==3){
            $('#lighter_'+msg.msg_id).click(function(){
                $(this).attr('href',$("#img_"+msg.msg_id).attr('src'));
                $(this).lighter();return false;
            });
        }
        if (msg.content.type==4){
            $("#au_"+msg.msg_id).click(function(){
                var audioElement = document.createElement('audio');
                audioElement.setAttribute('src',blodurl($(this).data("voice"),"audio/mpeg"));
                audioElement.play();
            });
        }
    },
    render: function() {
        this.scrollToBottom();
        if (this.messageToSend.trim() !== '') {
            var template = $("#message-template").html();
            var context = {
                toUser:(elt.tagsinput('items').length == 1)?send_last_user:"多个用户",
                messageOutput: this.messageToSend,
                time: this.getCurrentTime()
            };
            $.tmpl(template,context).appendTo(this.$chatHistoryList);
            this.scrollToBottom();
            this.$textarea.val('');
        }
    },

    addMessage: function() {
        this.messageToSend = this.$textarea.val()
        if(this.messageToSend!=''){
            send_to_users = elt.tagsinput('items').slice(0);
            body = this.messageToSend;
            if(send_to_users.length == 0){
                alert("请选择将信息发给谁！");
                return false;
            }
            send_wx_users(body);
            $("#message-to-send").val('');
        }
        this.render();
    },
    addMessageEnter: function(event) {
        // enter was pressed
        if (event.keyCode === 13) {
            this.addMessage();
        }
    },
    scrollToBottom: function() {
        this.$chatHistory.scrollTop(this.$chatHistory[0].scrollHeight);
    },
    getCurrentTime: function(timestamp =0) {
        if(timestamp>0){
            return new Date(timestamp).toLocaleTimeString().
                replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3");
        }else{
            return new Date().toLocaleTimeString().
                replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3");
        }
    }

};

function init_ws(){
    ws = new WebSocket(ws_url);
    ws.onopen = function () {
        heartCheck.start();
     };
    ws.onmessage = function (event) {
        heartCheck.reset();
        var json = JSON.parse(event.data);
            if(json.heartcheck == '6469616e6e616f3531'){

            }else if (json.msg_type_id == 4){
                chat.wsRenderFriend(json);
            }else{
                chat.wsRenderSelf(json);
            }
            chat.scrollToBottom();
    };
    ws.onclose = function () {
        init_ws();
    };
    ws.onerror = function () {
        init_ws();
    };
}

function send_wx_users(msg_body){
    if (send_to_users.length > 0) {
        curr_user = send_to_users.pop();
        send_last_user = curr_user['text'];
        $.post("weixin/sendmsg",{to_user:curr_user["value"],body:msg_body},function(res){
            sleep(1000).then(() => {send_wx_users(msg_body);});
        },"json");
    }
}


$(function(){
    chat.init();
    init_ws();
});