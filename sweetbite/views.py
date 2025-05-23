from django.shortcuts import render


def handler404(request, exception):
    """ Error Handler 404 - Page Not Found """
    return render(request, "errors/404.html", status=404)


def handler403(request, exception):
    """
    Custom view for handling 403 Forbidden errors.
    """
    return render(request, 'errors/403.html', status=403)


def handler500(request, exception):
    """
    Custom view for handling 500 Internal server errors.
    """
    return render(request, 'errors/500.html', status=500)

