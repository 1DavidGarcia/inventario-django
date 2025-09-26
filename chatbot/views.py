import os
import subprocess
from django.http import FileResponse, HttpResponseServerError
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

def enviar_paquetes(request):
    if request.method == 'POST':
        destino = request.POST.get('destino')
        paquetes = request.POST.getlist('paquetes[]')

        confirmacion = {
            'estado': 'enviado',
            'destino': destino,
            'paquetes': paquetes,
            'codigo_confirmacion': 'SKY-' + str(len(paquetes)) + '-OK'
        }

        return JsonResponse(confirmacion)

    return render(request, 'enviar_paquetes.html')


def index(request):
    return render(request, 'index.html')

def backup_inventario(request):
    mysqldump_path = r"C:\Program Files\MariaDB 12.0\bin\mysqldump.exe"  # ← ajusta según tu sistema
    backup_path = os.path.join(settings.BASE_DIR, 'backup_inventario.sql')  # ← define la ruta del archivo

    try:
        with open(backup_path, 'w') as output_file:
            result = subprocess.run([
                mysqldump_path,
                '-u', 'root',
                '-pmariadb',
                'django',
                'producto', 'sucursal'
            ], stdout=output_file, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            return HttpResponseServerError(f"Error al generar el backup:\n{result.stderr}")

        if not os.path.exists(backup_path):
            return HttpResponseServerError("El archivo de respaldo no fue creado.")

        return FileResponse(open(backup_path, 'rb'), as_attachment=True, filename='backup_inventario.sql')

    except Exception as e:
        return HttpResponseServerError(f"Error inesperado: {str(e)}")
