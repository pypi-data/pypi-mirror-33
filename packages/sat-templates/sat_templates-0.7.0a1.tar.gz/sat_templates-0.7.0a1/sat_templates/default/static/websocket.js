/*
SàT templates: suit of templates for Salut à Toi
Copyright (C) 2017 Jérôme Poisson (goffi@goffi.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/* websocket handler */


//TODO: retry websocket instead of reload
function WSHandler(url, token, debug=false) {
    var socket = new WebSocket(url, 'libervia_page_' + token );
    var retried = 0;

    var errorHandler = function(error) {
        if (retried > 20) {
            console.error("Too many tries, can't start websocket");
            alert("Dynamic connection with server can't be established, please try to reload this page in a while or contact your service administrator");
            return;
        }
        var delay = Math.floor((Math.random() * 10) + 1) + 30 * Math.min(retried, 6);
        notifyRetry(delay, function() {
            retried++;
            socket = new WebSocket(url, 'libervia_page_' + token );
            socket.addEventListener('error', errorHandler);
        });
    };

    socket.addEventListener('error', errorHandler);

    if (debug) {
        socket.addEventListener('message', function(event) {
            console.log('WS in <== ', JSON.parse(event.data));
        });
    }

    socket.addEventListener('message', function(event) {
        try {data = JSON.parse(event.data);}
        catch (e) {
            console.warn('invalid websocket message received: %s', e);
            return;
        }
        switch (data.type) {
            case 'reload':
                location.reload(true);
                break;
            case 'dom':
                selected_element = document.body.querySelector(data.selectors);
                switch (data.update_type) {
                    case 'append':
                        var template = document.createElement('template');
                        template.innerHTML = data.html.trim();
                        new_element = template.content.firstChild;
                        selected_element.appendChild(new_element);
                        break;
                    default:
                        console.warn('Unknown DOM update type: %s', data.update_type);
                }
                break;
            default:
                console.warn('Unknown data type: %s', data.type);
        }
    });

    socket.addEventListener('open', function (event) {
        console.log('Websocket opened');
        retried = 0;
    }.bind(this));

    this.send = function(data) {
        if (debug) {
            console.log('WS out ==> ', data);
        }
        socket.send(JSON.stringify(data));
    };

    function notifyRetry(timeout, retryCb) {
        /* Show a notification dialog informing the user that server can't be reach
         * and call retryCb after timeout seconds.
         * A "retry now" link allows to retry immediately"
         *
         * @param timeout(int): delay before retrying, in seconds
         * @param retryCb(function): function to call when retrying
         */
        var startTime = Date.now() / 1000;
        var retryIntervalID;
        var notif = document.createElement("div");
        notif.setAttribute('class', 'notification retry');
        //FIXME: we use English without translation for now, must be changed when we can use gettext in Libervia pages
        notif.innerHTML = "<p>Can't reach the server, retrying in <span id='retry_counter'></span> seconds</p><p><a id='retry_now'>retry now</a></p>";
        document.body.appendChild(notif);
        var retryCounter = document.getElementById('retry_counter');
        retryCounter.textContent = timeout;

        var retry = function () {
            clearInterval(retryIntervalID);
            notif.parentNode.removeChild(notif);
            retryCb();
        };

        var updateTimer = function () {
            var elapsed = Math.floor(Date.now() / 1000 - startTime);
            var remaining = timeout - elapsed;
            if (remaining < 0) {
                retry();
            }
            else {
                retryCounter.textContent = remaining;
            }
        };

        var retryNow = document.getElementById('retry_now');
        retryNow.addEventListener('click', function(){
            retry();
        });

        retryIntervalID = setInterval(updateTimer, 1000);
    }
}
