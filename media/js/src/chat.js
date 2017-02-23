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
    '../libs/commonmark.min',
    '../libs/linkify/linkify.min',
    '../libs/linkify/linkify-html.min',
    '../libs/js-emoji/emoji.min'
], function(domReady, $, commonmark, linkify, linkifyHtml, emoji) {

    var renderMarkdown = function(text) {
        var reader = new commonmark.Parser();
        var writer = new commonmark.HtmlRenderer();
        if (window.STATIC_URL) {
            emoji.sheet_path = window.STATIC_URL +
                'emoji-data/sheet_apple_64.png';
        }
        emoji.use_sheet = true;
        // Temporary workaround for img_path issue:
        // https://github.com/iamcal/js-emoji/issues/47
        emoji.img_sets[emoji.img_set].sheet = emoji.sheet_path;

        var parsed = reader.parse(text);
        var rendered = writer.render(parsed);
        if (typeof window.linkifyHtml === 'function') {
            rendered = window.linkifyHtml(rendered);
        }
        if (typeof emoji.replace_colons === 'function') {
            rendered = emoji.replace_colons(rendered);
        }
        return rendered;
    };

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
            '<div class="alert"><b>Connection closed. trying again in ' +
                currentRefresh / 1000 + ' seconds</b></div>'));
        setTimeout(connectSocket,currentRefresh);
    };

    var connectSocket = function() {
        conn = new WebSocket(window.websocketsBase + '?token=' + window.token);
        conn.onclose = requestFailed;
        conn.onmessage = onMessage;
        conn.onopen = function(evt) {
            currentRefresh = defaultRefresh;
            appendLog($('<div class="alert alert-info"><b>' +
                        'Connected to server.</b></div>'));
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
                     renderMarkdown(data[attr]) + '</div>');
        appendLog(entry);
    };

    function appendLog(msg) {
        var d = log[0];
        var doScroll = d.scrollTop === d.scrollHeight - d.clientHeight;
        msg.appendTo(log);
        if (doScroll) {
            d.scrollTop = d.scrollHeight - d.clientHeight;
        }
    }

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
        } else {
            appendLog($('<div><b>Your browser does not support ' +
                        'WebSockets.</b></div>'));
        }
    });
});
