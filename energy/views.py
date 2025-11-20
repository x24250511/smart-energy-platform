from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from accounts.models import EnergyUser
from .models import Transaction
from .cloud_services import cloud_manager

@login_required
def dashboard(request):
    user = request.user
    surplus = user.calculate_surplus()
    deficit = user.calculate_deficit()
    recent_transactions = Transaction.objects.filter(from_user=user)[:10]
    
    context = {
        'user': user,
        'surplus': surplus,
        'deficit': deficit,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'energy/dashboard.html', context)

@login_required
def update_energy(request):
    user = request.user
    
    if request.method == 'POST':
        generated = float(request.POST.get('generated', 0))
        consumed = float(request.POST.get('consumed', 0))
        
        user.generated = generated
        user.consumed = consumed
        user.save()
        
        messages.success(request, 'Energy data updated')
        return redirect('energy:dashboard')
    
    context = {
        'user': user,
        'surplus': user.calculate_surplus(),
        'deficit': user.calculate_deficit(),
    }
    return render(request, 'energy/update_energy.html', context)

@login_required
def buyback_view(request):
    user = request.user
    surplus = user.calculate_surplus()
    
    if request.method == 'POST':
        if surplus <= 0:
            messages.error(request, 'No surplus energy available')
            return redirect('energy:buyback')
        
        kwh_amount = float(request.POST.get('amount', 0))
        
        if kwh_amount <= 0 or kwh_amount > surplus:
            messages.error(request, 'Invalid amount')
            return redirect('energy:buyback')
        
        buyback_rate = 0.15
        credits_earned = kwh_amount * buyback_rate
        
        with transaction.atomic():
            user.consumed += kwh_amount
            user.credits += credits_earned
            user.save()
            
            Transaction.objects.create(
                from_user=user,
                amount=kwh_amount,
                transaction_type='buyback'
            )
            
            try:
                result = cloud_manager.process_transaction_with_cloud(
                    user, 'buyback', kwh_amount
                )
                messages.success(request, f'Buyback successful: {kwh_amount} kWh for {credits_earned} credits. {result["message"]}')
            except:
                messages.success(request, f'Buyback successful: {kwh_amount} kWh for {credits_earned} credits')
        
        return redirect('energy:dashboard')
    
    context = {'user': user, 'surplus': surplus}
    return render(request, 'energy/buyback.html', context)

@login_required
def loan_view(request):
    user = request.user
    surplus = user.calculate_surplus()
    other_users = EnergyUser.objects.exclude(id=user.id)
    
    if request.method == 'POST':
        if surplus <= 0:
            messages.error(request, 'No surplus energy available')
            return redirect('energy:loan')
        
        recipient_id = int(request.POST.get('recipient'))
        kwh_amount = float(request.POST.get('amount', 0))
        
        if kwh_amount <= 0 or kwh_amount > surplus:
            messages.error(request, 'Invalid amount')
            return redirect('energy:loan')
        
        recipient = EnergyUser.objects.get(id=recipient_id)
        loan_rate = 0.10
        credits_earned = kwh_amount * loan_rate
        
        with transaction.atomic():
            user.consumed += kwh_amount
            user.credits += credits_earned
            user.save()
            
            recipient.generated += kwh_amount
            recipient.save()
            
            Transaction.objects.create(
                from_user=user,
                to_user=recipient,
                amount=kwh_amount,
                transaction_type='loan'
            )
            
            try:
                result = cloud_manager.process_transaction_with_cloud(
                    user, 'loan', kwh_amount
                )
                messages.success(request, f'Loan successful: {kwh_amount} kWh to {recipient.name}. {result["message"]}')
            except:
                messages.success(request, f'Loan successful: {kwh_amount} kWh to {recipient.name}')
        
        return redirect('energy:dashboard')
    
    context = {'user': user, 'surplus': surplus, 'other_users': other_users}
    return render(request, 'energy/loan.html', context)

@login_required
def donation_view(request):
    user = request.user
    surplus = user.calculate_surplus()
    
    if request.method == 'POST':
        if surplus <= 0:
            messages.error(request, 'No surplus energy available')
            return redirect('energy:donation')
        
        recipient_energy_number = request.POST.get('energy_number', '').strip()
        kwh_amount = float(request.POST.get('amount', 0))
        
        if kwh_amount <= 0 or kwh_amount > surplus:
            messages.error(request, 'Invalid amount')
            return redirect('energy:donation')
        
        try:
            recipient = EnergyUser.objects.get(energy_number=recipient_energy_number)
            
            if recipient.id == user.id:
                messages.error(request, 'Cannot donate to yourself')
                return redirect('energy:donation')
            
            with transaction.atomic():
                user.consumed += kwh_amount
                user.save()
                
                recipient.generated += kwh_amount
                recipient.save()
                
                Transaction.objects.create(
                    from_user=user,
                    to_user=recipient,
                    amount=kwh_amount,
                    transaction_type='donation'
                )
                
                try:
                    result = cloud_manager.process_transaction_with_cloud(
                        user, 'donation', kwh_amount
                    )
                    messages.success(request, f'Donation successful: {kwh_amount} kWh donated to {recipient.name}. {result["message"]}')
                except:
                    messages.success(request, f'Donation successful: {kwh_amount} kWh donated to {recipient.name}')
            
            return redirect('energy:dashboard')
            
        except EnergyUser.DoesNotExist:
            messages.error(request, f'Energy number {recipient_energy_number} not found')
            return redirect('energy:donation')
    
    context = {'user': user, 'surplus': surplus}
    return render(request, 'energy/donation.html', context)
