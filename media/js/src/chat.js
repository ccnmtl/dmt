require([
    'domReady',
    'jquery',
    'utils/markdown_renderer'
], function(domReady, $, MarkdownRenderer) {
    var conn;
    var log = $('#log');

    var currentRefresh = 1000;
    var defaultRefresh = 1000;
    var maxRefresh = 1000 * 5 * 60; // 5 minutes
    var renderer = new MarkdownRenderer();

    var updateToken = function() {
        $.ajax({
            url: window.freshTokenURL,
            type: 'get',
            dateType: 'json',
            error: function(evt) {
                setTimeout(updateToken, currentRefresh);
            },
            success: function(d) {
                window.token = d.token;
            }
        });
    };

    var requestFailed = function(evt) {
        // circuit breaker pattern for failed requests
        // to ease up on the server when it's having trouble
        updateToken();
        currentRefresh = 2 * currentRefresh; // double the refresh time
        if (currentRefresh > maxRefresh) {
            currentRefresh = maxRefresh;
        }
        appendLog($(
            '<div class="alert"><strong>Connection closed. trying again in ' +
                currentRefresh / 1000 + ' seconds</strong></div>'));
        setTimeout(connectSocket,currentRefresh);
    };

    var connectSocket = function() {
        conn = new WebSocket(window.websocketsBase + '?token=' + window.token);
        conn.onclose = requestFailed;
        conn.onmessage = onMessage;
        conn.onopen = function(evt) {
            currentRefresh = defaultRefresh;
            appendLog($('<div class="alert alert-info"><strong>' +
                        'Connected to server.</strong></div>'));
        };
    };

    var onMessage = function(evt) {
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);

        var entry = $('<div/>');
        entry.addClass('row');
        var d = new Date();
        var hours = d.getHours();
        var minutes = d.getMinutes();

        if (minutes < 10) {
            minutes = '0' + minutes;
        }
        entry.append('<div class="col-md-1 timestamp">' + hours + ':' +
                     minutes + '</div>');
        entry.append('<div class="col-md-2 nick"><a href="' + data.userURL +
                     '">' + data.fullname + '</a></div>');
        var attr = 'message_text';
        entry.append('<div class="col-md-9 ircmessage">' +
                     renderer.render(data[attr]) + '</div>');
        appendLog(entry);
    };

    var appendLog = function(msg) {
        var d = log[0];
        var doScroll = d.scrollTop === d.scrollHeight - d.clientHeight;
        msg.appendTo(log);
        if (doScroll) {
            d.scrollTop = d.scrollHeight - d.clientHeight;
        }
    };

    domReady(function() {
        if ($('#msg_form').length < 1) {
            return;
        }

        $('#msg_form').submit(function() {
            var msg = $('#text-input');
            $.ajax({
                type: 'POST',
                url: window.postURL,
                data: {'text': msg.val()},
                success: function() {
                    msg.val('');
                },
                error: function() {
                    alert('post failed');
                }
            });
            return false;
        });

        if (window.WebSocket) {
            connectSocket();
        } else {
            appendLog($('<div><strong>Your browser does not support ' +
                        'WebSockets.</strong></div>'));
        }
    });
});
