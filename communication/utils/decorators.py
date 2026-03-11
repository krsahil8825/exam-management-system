"""
communication.utils.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Defines decorators for access control in communication views.
"""

from functools import wraps
from django.http import Http404
from django.shortcuts import get_object_or_404

from accounts.utils.decorators import employee_required
from ..models import Messages


def message_participant_required(view_func):
    """
    Allow access only if the logged-in employee
    is the sender or receiver of the message.
    """

    @employee_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        slug = kwargs.get("slug")
        message = get_object_or_404(Messages, slug=slug)
        employee = request.user.employee_profile

        # Hide message existence if user is not a participant
        if employee != message.sender and employee != message.receiver:
            raise Http404("Message not found.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
