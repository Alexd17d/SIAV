import matplotlib.pyplot as plt
import os

# 1. ASEGURAR QUE EXISTA LA CARPETA DATA DENTRO DEL MIS
if not os.path.exists("data"):
    os.makedirs("data")

# ============================================================
# 2. INICIALIZACIÓN DE VARIABLES PARA LOS 8 KPIs
# ============================================================
total_vehiculos = 0
sin_revision = 0
aprobado_2da = 0
aprobado_3ra = 0

conteo_livianos = 0
conteo_pesados = 0
conteo_motos = 0

recaudacion_real = 0.0
recaudacion_proyectada_total = 0.0

# Variables para el NUEVO KPI 5 Avanzado (Riesgo Mecánico)
reinspecciones_autos_viejos = 0  # Más de 15 años de antigüedad (fabricados antes de 2011)
reinspecciones_autos_nuevos = 0  # Menos de 15 años de antigüedad (fabricados desde 2011)

# Estructuras dinámicas para almacenar conteos y cálculos de soporte
antiguedad_por_tipo = {"pesado": 0.0, "liviano": 0.0, "moto": 0.0}
conteos_por_tipo = {"pesado": 0, "liviano": 0, "moto": 0}
avaluo_total_por_tipo = {"pesado": 0.0, "liviano": 0.0, "moto": 0.0}
matriculados_por_tipo = {"pesado": 0, "liviano": 0, "moto": 0}

# KPI 8: Control de carga horaria/calendario por último dígito de placa
saturacion_placa = {i: 0 for i in range(10)}

# ============================================================
# 3. EXTRACCIÓN Y PROCESAMIENTO DE DATOS EN UN SOLO BUCLE (ETL)
# ============================================================
ruta_archivo = "../TPS/data/vehiculos.txt"
print("[SISTEMA MIS] Leyendo base de datos transaccional del TPS...")

with open(ruta_archivo, "r") as archivo:
    for linea in archivo:
        linea = linea.strip()
        if not linea or len(linea.split(",")) < 9:
            continue
            
        datos = linea.split(",")
        try:
            placa = datos[1]
            anio = int(datos[3])
            tipo = datos[4]
            r1 = int(datos[6])
            r2 = int(datos[7])
            r3 = int(datos[8])
        except ValueError:
            continue

        total_vehiculos += 1
        es_matriculado = (r1 == 1 or r2 == 1 or r3 == 1)
        antiguedad_anios = 2026 - anio
        
        # --- LÓGICA DE REVISIONES (KPI 1 y KPI 2) ---
        if not es_matriculado:
            sin_revision += 1
        elif r2 == 1:
            aprobado_2da += 1
        elif r3 == 1:
            aprobado_3ra += 1

        # --- LÓGICA DE CLASIFICACIÓN (KPI 3 y KPI 6) ---
        if tipo == "liviano":
            conteo_livianos += 1
        elif tipo == "pesado":
            conteo_pesados += 1
        elif tipo == "moto":
            conteo_motos += 1

        if tipo in conteos_por_tipo:
            conteos_por_tipo[tipo] += 1
            antiguedad_por_tipo[tipo] += antiguedad_anios
            
        # --- LÓGICA FINANCIERA (KPI 4 y KPI 7) ---
        tasa_base = 200.0 if tipo == "pesado" else 25.0
        valor_matricula = tasa_base + (antiguedad_anios * 5.0) + (0.0 if es_matriculado else 50.0)
        recaudacion_proyectada_total += valor_matricula
        
        if es_matriculado:
            recaudacion_real += valor_matricula
            matriculados_por_tipo[tipo] += 1
            avaluo_total_por_tipo[tipo] += valor_matricula

        # --- NUEVA LÓGICA AVANZADA: CRUCE DE RIESGO MECÁNICO (KPI 5) ---
        # Si el auto necesitó ir a re-inspección (2da o 3ra cita)
        if r2 == 1 or r3 == 1:
            if antiguedad_anios > 15:
                reinspecciones_autos_viejos += 1
            else:
                reinspecciones_autos_nuevos += 1

        # --- LÓGICA DE CALENDARIO DE PLACAS (KPI 8) ---
        try:
            ultimo_digito = int(placa[-1])
            saturacion_placa[ultimo_digito] += 1
        except ValueError:
            continue

# Cálculos globales de salida
matriculados_totales = aprobado_2da + aprobado_3ra
porcentaje_morosidad = (sin_revision / total_vehiculos) * 100 if total_vehiculos > 0 else 0
tipos_lista = list(antiguedad_por_tipo.keys())

print(f"[OK] {total_vehiculos:,} registros transaccionales consolidados en memoria.\n")


# ============================================================
# BLOQUE A: REPORTES PROGRAMADOS (ROUTINE REPORTS)
# ============================================================
print("[MIS] Exportando Reportes Programados...")

# KPI 1: Control de Matriculación Anual
plt.figure(figsize=(6, 4))
plt.bar(['Matriculados', 'Morosos'], [matriculados_totales, sin_revision], color=['green', 'red'])
plt.title(f'KPI 1: Control de Matriculación Anual\n(Morosidad: {porcentaje_morosidad:.2f}%)')
plt.ylabel('Cantidad de Vehículos')
plt.savefig('data/kpi1.png')
plt.close()

# KPI 4: Recaudación Real vs Proyectada
plt.figure(figsize=(6, 4))
valores_kpi4 = [recaudacion_real, recaudacion_proyectada_total - recaudacion_real]
plt.bar(['Recaudado Real ($)', 'Fuga Morosidad ($)'], valores_kpi4, color=['#2ecc71', '#e74c3c'])
plt.title('KPI 4: Estado Financiero del Presupuesto Anual')
plt.ylabel('Dólares ($)')
for i, v in enumerate(valores_kpi4):
    plt.text(i, v + (max(valores_kpi4)*0.01), f"${v:,.2f}", ha='center', fontweight='bold')
plt.savefig('data/kpi4.png')
plt.close()

# KPI 8: Tasa de Saturación por Dígito de Placa
plt.figure(figsize=(8, 4))
plt.bar([f"Dígito {k}" for k in saturacion_placa.keys()], saturacion_placa.values(), color='#34495e')
plt.title('KPI 8: Tasa de Saturación de Trámites por Calendario de Placas')
plt.ylabel('Cantidad de Vehículos')
plt.savefig('data/kpi8.png')
plt.close()


# ============================================================
# BLOQUE B: REPORTES DE INDICADORES CLAVE (KEY-INDICATOR REPORTS)
# ============================================================
print("[MIS] Exportando Reportes de Indicadores Clave...")

# KPI 2: Curva de Eficiencia de Citas
plt.figure(figsize=(7, 4))
plt.plot(['1ra Cita', '2da Cita', '3ra Cita'], [0, aprobado_2da, aprobado_3ra], marker='o', color='#2980b9', linewidth=3)
plt.title('KPI 2: Eficiencia de Aprobación en Plantas de Revisión')
plt.ylabel('Vehículos Aprobados')
plt.savefig('data/kpi2.png')
plt.close()

# KPI 3: Distribución del Parque Automotor
plt.figure(figsize=(5, 5))
valores_kpi3 = [conteo_livianos, conteo_pesados, conteo_motos]
plt.pie(valores_kpi3, labels=['Livianos', 'Pesados', 'Motos'], autopct='%1.1f%%', startangle=140, colors=['lightblue', 'orange', 'yellow'])
plt.title('KPI 3: Distribución del Parque Automotor Registrado')
plt.savefig('data/kpi3.png')
plt.close()

# --- NUEVO KPI 5: TASA DE RECHAZO CRÍTICO POR ANTIGÜEDAD COMBINADA ---
plt.figure(figsize=(6, 4))
valores_kpi5 = [reinspecciones_autos_viejos, reinspecciones_autos_nuevos]
plt.bar(['Modelos Viejos (>15 años)', 'Modelos Nuevos (<=15 años)'], valores_kpi5, color=['#e67e22', '#3498db'])
plt.title('KPI 5: Índice de Vulnerabilidad y Re-inspección por Antigüedad', fontweight='bold')
plt.ylabel('Cantidad de Vehículos Reprobados en 1ra Cita')
for i, v in enumerate(valores_kpi5):
    plt.text(i, v + (max(valores_kpi5)*0.01), f"{v:,} ud", ha='center', fontweight='bold')
plt.savefig('data/kpi5.png')
plt.close()

# KPI 6: Antigüedad Promedio del Parque Automotor
plt.figure(figsize=(7, 4))
promedios_edad = [antiguedad_por_tipo[t] / conteos_por_tipo[t] if conteos_por_tipo[t] > 0 else 0 for t in tipos_lista]
plt.bar(['Pesados', 'Livianos', 'Motos'], promedios_edad, color=['#34495e', '#9b59b6', '#f1c40f'])
plt.title('KPI 6: Edad Promedio del Parque Vehicular')
plt.ylabel('Años de Antigüedad')
for i, v in enumerate(promedios_edad):
    plt.text(i, v + 0.2, f"{v:.1f} años", ha='center', fontweight='bold')
plt.savefig('data/kpi6.png')
plt.close()

# KPI 7: Ticket Promedio de Recaudación por Trámite Exitoso
plt.figure(figsize=(7, 4))
ticket_promedio = [avaluo_total_por_tipo[t] / matriculados_por_tipo[t] if matriculados_por_tipo[t] > 0 else 0 for t in tipos_lista]
plt.bar(['Pesados', 'Livianos', 'Motos'], ticket_promedio, color=['#1abc9c', '#e67e22', '#e74c3c'])
plt.title('KPI 7: Ticket Promedio Cobrado por Tipo de Vehículo')
plt.ylabel('Valor Promedio ($)')
for i, v in enumerate(ticket_promedio):
    plt.text(i, v + 2, f"${v:.2f}", ha='center', fontweight='bold')
plt.savefig('data/kpi7.png')
plt.close()

print("\n[PROCESO COMPLETADO] Los 8 KPIs avanzados han sido guardados individualmente en 'MIS/data/'.")