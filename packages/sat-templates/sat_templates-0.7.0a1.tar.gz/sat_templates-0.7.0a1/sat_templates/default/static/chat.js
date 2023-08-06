/* SàT Template: Chat page handling
 *
 * Copyright (C) 2017 Jérôme Poisson (goffi@goffi.org)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */


var msgInput = document.getElementById('message_input');
var messages = document.getElementById('messages');
const messagesTransitionOri = messages.style.transition;

msgInput.addEventListener('keypress', function(event) {
    if (event.which == 13 && !event.shiftKey) {
        if (messages.style.height !== '100%') {
            messages.style.transition = messagesTransitionOri;
            setTimeout(function() {
                messages.style.transition = 'initial';
                messages.scrollTop = messages.scrollHeight;
            }, 1000);
            messages.style.height = "100%";
        }
        if (!this.value.trim()) {
            return;
        }
        socket.send({'type': 'msg',
                     'body': this.value});
        this.value = '';
        event.preventDefault();
    }}
);

var mutationCb = function(mutationsList) {
    scrollPos = messages.scrollTop + messages.clientHeight;
    if (messages.lastChild.offsetTop - scrollPos - 10 <= 0) {
        // we auto scroll only if we are at the bottom of the page
        // else the use is probably checking history
        // Note thas this doesn't take margin into account,
        // we suppose margin to be 0 for messages children
        messages.scrollTop = messages.scrollHeight;
    }
};

var observer = new MutationObserver(mutationCb);

observer.observe(messages, { childList: true });
// we want to start with scrolling at bottom
messages.scrollTop = messages.scrollHeight;
messages.style.transition = 'initial';
