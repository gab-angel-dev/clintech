from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import htmx_login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from apps.accounts.models import CustomUser
from .forms import AdminEditForm, AdminCreationForm
from django.contrib.auth.forms import SetPasswordForm



def _admin_ativos() -> int:
    return CustomUser.objects.filter(is_active=True).count()



@login_required
def equipe_view(request):
    admins = CustomUser.objects.all().order_by('-created_at')
    return render(request, 'equipe/equipe.html',
            {'admins': admins}
    )


@login_required
def admin_novo_view(request):
    form = AdminCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()

        return redirect('equipe:equipe')

    return render(request, 'equipe/admin_novo.html',
            {'form': form}
    )


@login_required
def admin_editar_view(request, pk):
    admin = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        form = AdminEditForm(request.POST, instance=admin)

        if form.is_valid():
            form.save()

        return redirect('equipe:equipe')
    
    else:
        form = AdminEditForm(instance=admin)

    return render(request, 'equipe/admin_editar.html', 
            {
                'form': form,
                'admin': admin
            }
    )



@login_required
def admin_senha_view(request, pk):
    admin = get_object_or_404(CustomUser, pk=pk)

    if request.method == "POST":
        form = SetPasswordForm(user=admin, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect('equipe:equipe')

    else:
        form = SetPasswordForm(user=admin)

    return render(request, 'equipe/admin_senha.html', {'form': form, 'admin': admin})


@login_required
@require_POST
def admin_toggle_ativo_view(request, pk):
    admin = get_object_or_404(CustomUser, pk=pk)

    # Impede desativar o último admin ativo do sistema.
    if admin.is_active and _admin_ativos() <= 1:
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'equipe/partials/admin_row.html', {
                'adm': admin,
                'erro': 'Não é possível desativar o único administrador ativo.',
            })
        return redirect('equipe:equipe')

    admin.is_active = not admin.is_active
    admin.save()

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'equipe/partials/admin_row.html', {'adm': admin})

    return redirect('equipe:equipe')


@htmx_login_required
@require_http_methods(['DELETE'])
def admin_deletar_view(request, pk):
    admin = get_object_or_404(CustomUser, pk=pk)

    # Bloqueia SÓ quando deletar ESSE admin reduziria os ativos a zero —
    # admin já inativo nunca cai nessa restrição, porque deletá-lo não
    # muda a contagem de admins ativos.
    if admin.is_active and _admin_ativos() <= 1:
        return HttpResponse(
            "Não é possível remover o único administrador ativo.",
            status=409,
        )

    admin.delete()
    return HttpResponse(status=200)