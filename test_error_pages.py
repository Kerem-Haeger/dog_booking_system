# Error Page Testing URLs
# Add these temporarily to your core/urls.py for testing error pages in development

from django.http import Http404
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.views.generic import TemplateView

def test_404(request):
    """Test 404 error page"""
    raise Http404("This is a test 404 error")

def test_500(request):
    """Test 500 error page"""
    raise Exception("This is a test 500 error")

def test_403(request):
    """Test 403 error page"""
    raise PermissionDenied("This is a test 403 error")

def test_400(request):
    """Test 400 error page"""
    raise SuspiciousOperation("This is a test 400 error")

# Add these to your urlpatterns for testing:
# path('test/404/', test_404, name='test_404'),
# path('test/500/', test_500, name='test_500'),
# path('test/403/', test_403, name='test_403'),
# path('test/400/', test_400, name='test_400'),
