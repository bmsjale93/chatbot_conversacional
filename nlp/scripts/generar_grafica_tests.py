import pandas as pd
import matplotlib.pyplot as plt
import os

# Rutas correctas dentro del contenedor
csv_path = "/app/test_reports/historico_tests.csv"
grafica_path = "/app/test_reports/historico_tests.png"

# Verificamos si existe el archivo CSV
if not os.path.exists(csv_path):
    print("[❌ ERROR] No existe el archivo histórico. No se genera gráfica.")
    exit(1)

# Cargamos los datos
df = pd.read_csv(csv_path, parse_dates=["fecha"])

# Comprobamos si hay suficientes datos
if df.shape[0] < 2:
    print("[⚠️ Aviso] Hay menos de 2 registros en el histórico. No se genera gráfica todavía.")
    exit(0)

# Creamos la gráfica
plt.figure(figsize=(10, 6))
plt.plot(df["fecha"], df["tests_ok"], marker='o', label="Tests OK")
plt.plot(df["fecha"], df["tests_fail"], marker='x', label="Tests Fallidos")

plt.title("Evolución de Tests - NLP Project")
plt.xlabel("Fecha")
plt.ylabel("Cantidad de Tests")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()

# Guardar la gráfica
plt.savefig(grafica_path)
print(f"✅ Gráfica generada correctamente en {grafica_path}")
