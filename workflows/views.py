"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.template import Template, Context
from django.template.loader import render_to_string

from .models import Wizard, Step, StepCompletion, ActionItem

template_cache = {}

def workflows_dashboard(request):
    context = {"assigned_wizards": _populate_wizard_list(request.user,Wizard.objects.get_user_assigned_wizards(request.user))}

    return render_to_string('workflows/dashboard.html', context=context, request=request)

@login_required
@permission_required("workflows.basic_access")
def index(request: WSGIRequest) -> HttpResponse:

    assigned_wizards = _populate_wizard_list(request.user,Wizard.objects.get_user_assigned_wizards(request.user))
    wizards = _populate_wizard_list(request.user,Wizard.objects.get_user_wizards(request.user))

    context = {"assigned_wizards": assigned_wizards,
               "wizards": wizards}

    return render(request, "workflows/index.html", context)

@login_required
@permission_required("workflows.basic_access")
def view_wizard_by_permalink(request: WSGIRequest, permalink: str, step_id: int=0) -> HttpResponse:

    wizard = get_object_or_404(Wizard, permalink=permalink)

    return _view_wizard(request, wizard, step_id)

@login_required
@permission_required("workflows.basic_access")
def view_wizard_by_id(request: WSGIRequest, wiz_id: int, step_id: int=0) -> HttpResponse:

    wizard = get_object_or_404(Wizard, pk=wiz_id)

    return _view_wizard(request, wizard, step_id)


def _view_wizard(request: WSGIRequest, wizard: Wizard, step_id: int) -> HttpResponse:
    
    if not request.user in wizard.users:
        raise PermissionDenied("You do not have permission to view this resource.")

    step_id = step_id - 1 if step_id > 0 else None
    c = True if request.POST.get('c') == 'true' else False
    s = int(request.POST.get('s',0))

    steps = []
    incomplete_steps = []
    current_step = None
    update_step = None

    for i, step in enumerate(wizard.steps.all()):
        step_dict = {'id': i+1,'step':step,'complete':step.is_complete(request.user, wizard),'checks':_calculate_step_checks(request.user, step),'visible':step.visiblity.is_complete(request.user) if step.visibility is not None else True}

        steps.append(step_dict)

        if step.pk == s:
            update_step = i

        if step_dict['complete']:
            continue

        incomplete_steps.append(i)

    if c and not steps[update_step]['complete']:
        StepCompletion.objects.update_or_create(user=request.user,wizard=wizard,step=Step.objects.get(pk=steps[update_step]['step'].pk))
        steps[update_step]['complete'] = True
        incomplete_steps.remove(update_step)

    if step_id is not None and update_step is None and step_id < len(steps):
        current_step = step_id
    elif len(incomplete_steps) > 0:
        current_step = incomplete_steps[0]

    if current_step is not None:
        step_pct_complete = steps[current_step]['step'].pct_complete(request.user, wizard)
    else:
        step_pct_complete = 1
        ActionItem.objects.update_or_create(user=request.user, wizard=wizard, defaults={"completed": True})

    context = {
        "user": request.user,
        "wizard": wizard,
        "steps":steps,
        "current_step": None if current_step is None else steps[current_step],
        "review": bool(step_id),
        "total_pct_complete": wizard.pct_complete(request.user) * 100,
        "step_pct_complete":  step_pct_complete * 100,
        }

    if current_step is None:
        context['body_text'] = _render_body_or_default(wizard.body, context)
    else:
        context['body_text'] = _render_body_or_default(steps[current_step]['step'].body, context)

    return render(request, "workflows/step.html", context)

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

def _populate_wizard_list(user: User, wizards):
    result = []
    for w in wizards:
        count = 0
        total = w.steps.count()
        for step in w.steps.all():
            count += step.is_complete(user, w)

        result.append({"wizard": w, "completion": w.is_complete(user), "percent": count/total*100, "count": count, "total": total})

    return result
