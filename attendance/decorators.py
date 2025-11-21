from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def sabha_type_required(allowed_types):
    """Decorator to check if user has access to specific sabha types"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            try:
                profile = request.user.userprofile
                user_types = profile.allowed_sabha_types
                
                # Check if user has access to any of the required types
                if isinstance(allowed_types, str):
                    allowed_types_list = [allowed_types]
                else:
                    allowed_types_list = allowed_types
                
                if any(t in user_types for t in allowed_types_list):
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("You don't have access to this sabha type")
            except:
                return HttpResponseForbidden("User profile not found")
        
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorator to restrict access to admin users only"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='Temple Admin').exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Admin access required")
    
    return _wrapped_view