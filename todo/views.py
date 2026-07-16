from django.shortcuts import redirect, render
from django.http import Http404
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task


# Create your views here.
def parse_due_at(value):
    if not value:
        return None
    return make_aware(parse_datetime(value))


def index(request):
    if request.method == "POST":
        task = Task(
            title=request.POST["title"],
            due_at=parse_due_at(request.POST["due_at"]),
        )
        task.save()

    if request.GET.get("order") == "due":
        tasks = Task.objects.order_by("due_at")
    else:
        tasks = Task.objects.order_by("-posted_at")

    now = timezone.localtime()
    has_overdue = any(
        not task.completed and task.is_overdue(now) for task in tasks
    )

    context = {"tasks": tasks, "now": now, "has_overdue": has_overdue}
    return render(request, "todo/index.html", context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        "task": task,
    }
    return render(request, "todo/detail.html", context)


def edit(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    if request.method == "POST":
        task.title = request.POST["title"]
        task.due_at = parse_due_at(request.POST["due_at"])
        task.completed = "completed" in request.POST
        task.save()
        return redirect("detail", task_id=task.pk)

    context = {
        "task": task,
    }
    return render(request, "todo/edit.html", context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    task.delete()
    return redirect("index")


def toggle(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    if request.method == "POST":
        task.completed = "completed" in request.POST
        task.save()

    return redirect("index")
