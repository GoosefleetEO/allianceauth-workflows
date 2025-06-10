"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.template import Template, Context

from .models import Wizard, Step, StepCompletion

template_cache = {}

@login_required
@permission_required("onboarding.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    assigned_wizards = Wizard.objects.get_user_assigned_wizards(request.user)
    wizards = Wizard.objects.get_user_wizards(request.user)

    context = {"assigned_wizards": assigned_wizards,
               "wizards": wizards}

    return render(request, "onboarding/index.html", context)

@login_required
@permission_required("onboarding.basic_access")
def view_wizard_by_permalink(request: WSGIRequest, permalink: str, step_id: int=0) -> HttpResponse:

    wizard = get_object_or_404(Wizard, permalink=permalink)

    return _view_wizard(request, wizard, step_id)

@login_required
@permission_required("onboarding.basic_access")
def view_wizard_by_id(request: WSGIRequest, wiz_id: int, step_id: int=0) -> HttpResponse:

    wizard = get_object_or_404(Wizard, pk=wiz_id)

    return _view_wizard(request, wizard, step_id)


def _view_wizard(request: WSGIRequest, wizard: Wizard, step_id: int) -> HttpResponse:
    
    if not request.user in wizard.users:
        raise PermissionDenied("You do not have permission to view this resource.")

    steps = []
    current_step = False
    next_step = False

    for i, step in enumerate(wizard.steps.all()):
        step_dict = {'id': i+1,'step':step,'complete':step.is_complete(request.user, wizard),'checks':_calculate_step_checks(request.user, step)}

        steps.append(step_dict)

        if i > 0 and i == step_id:
            next_step = step_dict
        elif i + 1 == step_id:
            current_step = step_dict

        if step_dict['complete']:
            continue

        if not current_step:
            current_step = step_dict
            continue

        if not next_step:
            next_step = step_dict


    if request.POST.get('c','') == 'true' and current_step and not step_id:
        StepCompletion.objects.create(user=request.user,wizard=wizard,step=Step.objects.get(pk=request.POST.get('s')))
        current_step = next_step

    if current_step:
        step_pct_complete = current_step['step'].pct_complete(request.user, wizard)
    else:
        step_pct_complete = 1

    context = {
        "user": request.user,
        "wizard": wizard,
        "steps":steps,
        "current_step": current_step,
        "review": bool(step_id),
        "total_pct_complete": wizard.pct_complete(request.user) * 100,
        "step_pct_complete":  step_pct_complete * 100,
        }

    if not current_step:
        context['body_text'] = _render_body_or_default(wizard.body, context)

        return render(request, "onboarding/final.html", context)

    context['body_text'] = _render_body_or_default(current_step['step'].body, context)

    return render(request, "onboarding/step.html", context)

def _render_body_or_default(body: str, context):
        if body and body in template_cache:
            body_template = template_cache.get(body)
        elif body:
            body_template = Template(body)
            template_cache[body] = body_template
        else:
            body_template = Template('')

        return body_template.render(Context(context))


def _calculate_step_checks(user: User, step: Step):
        checks = []
        if not step.is_selfguided:
            for check in step.checks.all():
                checks.append(
                    {'check':check,
                     'is_complete': check.is_complete(user),
                     'is_complete_detail': check.is_complete_detail(user)
                     }
                 )
        return checks
