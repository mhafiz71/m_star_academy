from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from applications.models import Application


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only staff members can access admin views"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        """Custom handling for non-staff users"""
        if self.request.user.is_authenticated:
            messages.error(self.request, 'You do not have permission to access the admin portal.')
            return redirect('core:home')
        return super().handle_no_permission()


class DashboardView(StaffRequiredMixin, TemplateView):
    """Admin dashboard with application statistics and metrics"""
    template_name = 'administration/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get application statistics
        total_applications = Application.objects.count()
        pending_applications = Application.objects.filter(status='pending').count()
        approved_applications = Application.objects.filter(status='approved').count()
        rejected_applications = Application.objects.filter(status='rejected').count()
        waitlist_applications = Application.objects.filter(status='waitlist').count()
        
        # Recent applications (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_applications = Application.objects.filter(created_at__gte=week_ago).count()
        
        # Applications by grade
        grade_stats = Application.objects.values('grade_applying_for').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent applications for display
        latest_applications = Application.objects.select_related().order_by('-created_at')[:5]
        
        context.update({
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'approved_applications': approved_applications,
            'rejected_applications': rejected_applications,
            'waitlist_applications': waitlist_applications,
            'recent_applications': recent_applications,
            'grade_stats': grade_stats,
            'latest_applications': latest_applications,
        })
        
        return context


class ApplicationListView(StaffRequiredMixin, ListView):
    """View for listing all applications with filtering and search"""
    model = Application
    template_name = 'administration/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Application.objects.all().order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status and status in ['pending', 'approved', 'rejected', 'waitlist']:
            queryset = queryset.filter(status=status)
        
        # Filter by grade
        grade = self.request.GET.get('grade')
        if grade:
            queryset = queryset.filter(grade_applying_for=grade)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student_first_name__icontains=search) |
                Q(student_last_name__icontains=search) |
                Q(reference_number__icontains=search) |
                Q(guardian_first_name__icontains=search) |
                Q(guardian_last_name__icontains=search) |
                Q(guardian_email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options to context
        context['status_choices'] = Application.STATUS_CHOICES
        context['grade_choices'] = Application.GRADE_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_grade'] = self.request.GET.get('grade', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context


class ApplicationDetailView(StaffRequiredMixin, DetailView):
    """View for displaying detailed application information"""
    model = Application
    template_name = 'administration/application_detail.html'
    context_object_name = 'application'
    
    def get_object(self):
        return get_object_or_404(Application, pk=self.kwargs['pk'])
    
    def post(self, request, *args, **kwargs):
        """Handle status updates"""
        try:
            application = self.get_object()
            new_status = request.POST.get('status')
            
            if new_status in ['pending', 'approved', 'rejected', 'waitlist']:
                old_status = application.status
                application.status = new_status
                application.save()
                
                # Log status change
                logger.info(
                    f'Application {application.reference_number} status changed from '
                    f'{old_status} to {new_status} by {request.user.username}'
                )
                
                messages.success(
                    request, 
                    f'Application {application.reference_number} status updated from '
                    f'{old_status} to {new_status}.'
                )
            else:
                logger.warning(
                    f'Invalid status update attempt: {new_status} by {request.user.username}'
                )
                messages.error(request, 'Invalid status selected.')
                
        except ValidationError as e:
            logger.error(f'Validation error during status update: {e}')
            messages.error(request, 'Invalid data provided. Please try again.')
            
        except DatabaseError as e:
            logger.error(f'Database error during status update: {e}')
            messages.error(request, 'Technical error occurred. Please try again.')
            
        except Exception as e:
            logger.error(f'Unexpected error during status update: {e}', exc_info=True)
            messages.error(request, 'An unexpected error occurred. Please try again.')
        
        return redirect('administration:application_detail', pk=application.pk)


@login_required
def custom_logout_view(request):
    """Custom logout view with success message"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('core:home')
