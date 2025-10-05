import os
import subprocess
from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path

from .models import (
    Inventario,
    InventarioCRUD,
    EnviosEnCurso,
    Usuario
)

def sucursales_view(request):
    return render(request, 'sucursales.html')

def login_view(request):
    return render(request, 'login.html')

def index(request):
    if not request.session.get('usuario'):
        return redirect('login')  # ← redirige si no hay sesión
    return render(request, 'index.html')      # ← dashboard real

# Cerrar sesión
def logout_view(request):
    request.session.flush()
    return redirect('index')

# Backup de base de datos
def backup_inventario(request):
    """
    Genera un backup con mysqldump y devuelve el archivo para descarga.
    Ajusta el PATH de mysqldump si es necesario.
    """
    # Ruta al mysqldump (ajusta si no es esa)
    mysqldump_path = Path(r"C:\Program Files\MariaDB 12.0\bin\mysqldump.exe")

    # Aseguramos que settings.BASE_DIR sea Path (por compatibilidad)
    base_dir = Path(settings.BASE_DIR)

    backup_path = base_dir / 'backup_inventario.sql'

    # Obtener credenciales desde settings.DATABASES en vez de hardcodear
    db_conf = settings.DATABASES.get('default', {})
    db_user = db_conf.get('USER', 'root')
    db_pass = db_conf.get('PASSWORD', '')  # si no hay password, dejar vacío
    db_name = db_conf.get('NAME', '')

    if not mysqldump_path.exists():
        return HttpResponseServerError(f"mysqldump no encontrado en: {mysqldump_path}")

    try:
        # Abrimos en modo binario para recibir stdout directo
        with backup_path.open('wb') as output_file:
            cmd = [
                str(mysqldump_path),
                '-u', str(db_user),
            ]
            # Si hay password configurado, lo agregamos como -pPASSWORD (sin espacio)
            if db_pass:
                cmd.append(f'-p{db_pass}')
            cmd.append(db_name)

            result = subprocess.run(cmd, stdout=output_file, stderr=subprocess.PIPE)

        if result.returncode != 0:
            stderr_text = result.stderr.decode(errors='replace') if isinstance(result.stderr, bytes) else str(result.stderr)
            return HttpResponseServerError(f"Error al generar el backup:\n{stderr_text}")

        if not backup_path.exists() or backup_path.stat().st_size == 0:
            return HttpResponseServerError("El archivo de respaldo no fue creado o está vacío.")

        return FileResponse(backup_path.open('rb'), as_attachment=True, filename='backup_inventario.sql')

    except Exception as e:
        return HttpResponseServerError(f"Error inesperado: {e}")

# CRUD de inventario
def inventario_crud(request):
    if 'usuario' not in request.session:
        return redirect('index')
    if request.method == 'POST':
        if 'agregar' in request.POST:
            InventarioCRUD.objects.create(
                producto=request.POST['producto'],
                sucursal=request.POST['sucursal'],
                cantidad=request.POST['cantidad']
            )
        elif 'editar' in request.POST:
            registro = InventarioCRUD.objects.get(id=request.POST['id'])
            registro.producto = request.POST['producto']
            registro.sucursal = request.POST['sucursal']
            registro.cantidad = request.POST['cantidad']
            registro.save()
        elif 'eliminar' in request.POST:
            InventarioCRUD.objects.get(id=request.POST['id']).delete()
        return redirect('inventario_crud')

    registros = InventarioCRUD.objects.all()
    return render(request, 'inventario_crud.html', {'registros': registros})

# Envío de paquetes
def enviar_paquetes(request):
    if 'usuario' not in request.session:
        return redirect('index')
    if request.method == 'POST':
        destino = request.POST.get('destino')
        paquete_id = request.POST.get('paquete')

        if not destino or not paquete_id:
            return JsonResponse({'error': 'Faltan datos'}, status=400)

        try:
            paquete = InventarioCRUD.objects.get(id=paquete_id)

            envio = EnviosEnCurso.objects.create(
                producto=paquete.producto,
                sucursal=paquete.sucursal,
                cantidad=paquete.cantidad,
                destino=destino,
                codigo_confirmacion=f"SKY-{paquete.id}-OK"
            )

            deleted_count, _ = paquete.delete()

            return JsonResponse({
                'estado': 'enviado',
                'destino': destino,
                'paquete': paquete.producto,
                'codigo_confirmacion': envio.codigo_confirmacion,
                'deleted_count': deleted_count
            })

        except InventarioCRUD.DoesNotExist:
            return JsonResponse({'error': 'Paquete no encontrado'}, status=404)

    paquetes_disponibles = InventarioCRUD.objects.all()
    return render(request, 'enviar_paquetes.html', {'paquetes': paquetes_disponibles})

# Resumen de inventario
def resumen_inventario(request):
    total_productos = InventarioCRUD.objects.aggregate(total=Sum('cantidad'))['total'] or 0
    sucursales = (
        InventarioCRUD.objects
        .values('sucursal')
        .annotate(total=Sum('cantidad'))
        .order_by('-total')
    )
    top_sucursal = sucursales[0]['sucursal'] if sucursales else 'Ninguna'

    return JsonResponse({
        'total_productos': total_productos,
        'top_sucursal': top_sucursal,
        'sucursales': list(sucursales)
    })


@csrf_exempt
def auth_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if action == 'register':
            if Usuario.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error'})
            Usuario.objects.create(
                username=username,
                password=password,
                nombre=request.POST.get('nombre'),
                correo=request.POST.get('correo')
            )
            return JsonResponse({'status': 'registro_ok'})

        else:  # login
            if Usuario.objects.filter(username=username, password=password).exists():
                request.session['usuario'] = username  # ← activa sesión
                return JsonResponse({'status': 'login_ok'})
            else:
                return JsonResponse({'status': 'error'})
