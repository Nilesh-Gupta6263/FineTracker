from django.urls import path
from django.views import View
from .views import RegisterView,DashboardView,TransactionCreateView,TransactionListView,GoalCreateView,Export_Transaction



urlpatterns = [
   path('register/',RegisterView.as_view(),name='register'),

   path('',DashboardView.as_view(),name='dashboard'),

   path('transaction/add/',TransactionCreateView.as_view(),name='add_transaction'),

   path('transaction_list/',TransactionListView.as_view(),name='transaction_list'),

   path('goal/add/',GoalCreateView.as_view(),name='goal_add'),

   path('generate-report',Export_Transaction.as_view(),name='export_transactions')


]
