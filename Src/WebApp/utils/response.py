import string
from flask import request, render_template
from .send_data import send_messages


def response_template(_request: request, template: string) -> render_template:
    send_messages.send(request)
    return render_template(template)
