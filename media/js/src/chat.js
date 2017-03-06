/* jscs:disable requireCamelCaseOrUpperCaseIdentifiers */

require.config({
    map: {
        // This configures jquery to not export the $ and jQuery global
        // variables.
        '*': {
            'jquery': 'jquery-private'
        },
        'jquery-private': {
            'jquery': 'jquery'
        }
    },
    paths: {
        // Major libraries
        jquery: '../libs/jquery/jquery-min',
        'jquery-private': '../libs/jquery/jquery-private',

        // Require.js plugins
        text: '../libs/require/text',
        domReady: '../libs/require/domReady'
    },
    urlArgs: 'bust=' +  (new Date()).getTime()
});

require([
    'domReady',
    'jquery',
    'utils/markdown_renderer'
], function(domReady, $, MarkdownRenderer) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        }
    });

    var conn;
    var log = $('#log');

    var currentRefresh = 1000;
    var defaultRefresh = 1000;
    var maxRefresh = 1000 * 5 * 60; // 5 minutes
    var renderer = new MarkdownRenderer();
    var heartbeatInterval = 10 * 1000;

    // indexed by username
    //   each entry is dict with status, fullname, lastHB time
    //   and any other fields we want to store there
    var usersPresent = {};

    var seen = function(username, fullname) {
        var timestamp = Date.now();
        usersPresent[username] = {
            'fullname': fullname,
            'lastSeen': timestamp,
            'status': 'online'
        };
    };

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

    var heartBeat = function() {
        $.ajax({
            type: 'POST',
            url: window.heartbeatURL,
            data: {},
            error: function() {
                appendLog($('<div class="alert"><strong>' +
                            'Heartbeat failed.</strong></div>'));
            }
        });
        // trigger the next heartbeat
        setTimeout(heartBeat, heartbeatInterval);
    };

    var onMessage = function(evt) {
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);

        if ('heartbeat' in data) {
            seen(data.username, data.fullname);
            return;
        }

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
            heartBeat();
        } else {
            appendLog($('<div><strong>Your browser does not support ' +
                        'WebSockets.</strong></div>'));
        }
    });
});
