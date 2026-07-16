from django.shortcuts import get_object_or_404, redirect, render
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

    now = timezone.now()
    has_overdue = False
    for task in tasks:
        task.is_due = task.due_at is not None
        task.is_overdue_now = task.is_overdue(now)
        if task.is_overdue_now and not task.completed:
            has_overdue = True

    context = {
        "tasks": tasks,
        "now": timezone.localtime(now),
        "has_overdue": has_overdue,
    }
    return render(request, "todo/index.html", context)


def detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    context = {
        "task": task,
        "is_overdue_now": task.is_overdue(timezone.now()),
    }
    return render(request, "todo/detail.html", context)


def edit(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

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
    task = get_object_or_404(Task, pk=task_id)

    task.delete()
    return redirect("index")


def toggle(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == "POST":
        task.completed = "completed" in request.POST
        task.save()

    return redirect("index")
