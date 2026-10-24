from django.shortcuts import render,HttpResponse,redirect
from django.views import View
from finance.forms import RegisterForm,TransactionForm,GoalForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from finance.models import Transaction,Goal
from django.db.models import Sum
from.admin import TransactionResource

from django.contrib import messages


class RegisterView(View):
    def get(self,request,*args, **kwargs):
        form = RegisterForm()
        return render(request,"finance/register.html",{'Form':form})

    def post(self,request,*args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            messages.success(request,'Account created Successfully!')
            return redirect("dashboard")
        return render(request, "finance/register.html", {'form': form})    

class DashboardView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        transactions = Transaction.objects.filter(user=request.user)
        goals = Goal.objects.filter(user=request.user)
        #calculate total Income and Expense

        total_income = Transaction.objects.filter(user=request.user,transaction_type='Income').aggregate(Sum('amount'))['amount__sum'] or 0

        total_expense = Transaction.objects.filter(user=request.user,transaction_type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0

        net_saving = total_income - total_expense
        remaining_savings = net_saving

        goal_progress = []
        for goal in goals:
            if remaining_savings >= goal.target_amount:
                goal_progress.append({'goal':goal,'progress':100})
                remaining_savings -= goal.target_amount
            elif remaining_savings > 0:
                progress = (remaining_savings / goal.target_amount) * 100
                goal_progress.append({
            'goal': goal,
            'progress': progress,
        })
                remaining_savings = 0
            else:
                goal_progress.append({'goal':goal, 'progress':0})    

        Context = {
            'transaction':transactions,
            'goal':goals,
            'total_income':total_income,
            'total_expense':total_expense,
            'net_saving':net_saving,
            'goal_progress':goal_progress,
        }
        return render(request,'finance/dashboard.html',Context) 

        
          
class TransactionCreateView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        form = TransactionForm()
        return render(request,'finance/transaction_form.html',{'Form':form})

    def post(self,request,*args, **kwargs):
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request,'Transaction Added Successfully!')
            return redirect('dashboard')
        return render(request,'finance/transaction_form.html',{'form':form})    
    

class TransactionListView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        Transactions = Transaction.objects.filter(user=request.user)
        return render(request,'finance/transaction_list.html',{'Transactions':Transactions})


class GoalCreateView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        form = GoalForm()
        return render(request,'finance/goal_form.html',{'Form':form})

    def post(self,request,*args, **kwargs):
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request,'Goal created Successfully!')
            return redirect('dashboard')
        return render(request,'finance/goal_form.html',{'form':form}) 

class Export_Transaction(View):
    def get(self,request,*args, **kwargs):
        user_transactions = Transaction.objects.filter(user=request.user)
        Transaction_Resource = TransactionResource()
        dataset = Transaction_Resource.export(queryset=user_transactions)

        excel_data = dataset.export('xlsx')

        #Create the httpresponse with correct MIME type for an excel File
        response = HttpResponse(excel_data,content_type='application/vnd.openxmlformat-officedocument.spreedsheetml.sheet')

    # set the header for downloading the file
        response['content-disposition'] = 'attachment;filename=transactions_report.xlsx'
        return response

    

    