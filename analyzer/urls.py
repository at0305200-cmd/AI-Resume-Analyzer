from django.urls import path
from . import views


urlpatterns = [

    # Home page
    path(
        "",
        views.home,
        name="home"
    ),

    # Resume history
    path(
        "history/",
        views.history,
        name="history"
    ),

    # Individual resume analysis
    path(
        "resume/<int:resume_id>/",
        views.resume_detail,
        name="resume_detail"
    ),

]