from dotenv import load_dotenv
import os
import requests
import matplotlib.pyplot as plt

load_dotenv()

API_KEY = os.getenv("API_KEY")
CODIGO_PAIS = 'EC'


#Funcion para obtener el historial de intensidad de carbono
def obtener_historial(codigo_pais, api_key):
    url = f'https://api.electricitymaps.com/v3/carbon-intensity/history?zone={codigo_pais}'
    headers = {'auth-token': api_key}
    
    response = requests.get(url, headers=headers)
   
    if response.status_code == 200:
        data = response.json()
        return data['history']  
    else:
        print(f'Error al obtener datos: {response.status_code}')
        return None

#Funcion para obtener la mezcla histórica de generación eléctrica
def obtener_mezcla_historica(codigo_pais, api_key):
    url = f'https://api.electricitymaps.com/v3/power-breakdown/history?zone={codigo_pais}'
    headers = {'auth-token': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Mezcla histórica en {codigo_pais}:")
        
        if data['history']:
            print(data['history'][0])
        return data['history']
    else:
        print(f'Error al obtener mezcla histórica: {response.status_code}')
        return None


historial = obtener_historial(CODIGO_PAIS, API_KEY)


#Grafico intensidad de carbono
if historial:
    horas = [h['datetime'][11:16] for h in historial]
    intensidades = [h['carbonIntensity'] for h in historial]

    min_idx = intensidades.index(min(intensidades))
    max_idx = intensidades.index(max(intensidades))

    plt.figure(figsize=(10,5))
    plt.plot(horas, intensidades, marker='o', color='#1f77b4')
    plt.scatter(horas[min_idx], intensidades[min_idx], color='green', label='Mínimo')
    plt.scatter(horas[max_idx], intensidades[max_idx], color='red', label='Máximo')
    plt.annotate(f'Mín: {intensidades[min_idx]}', (horas[min_idx], intensidades[min_idx]), textcoords="offset points", xytext=(0,10), ha='center', color='green')
    plt.annotate(f'Máx: {intensidades[max_idx]}', (horas[max_idx], intensidades[max_idx]), textcoords="offset points", xytext=(0,-15), ha='center', color='red')
    plt.fill_between(horas, intensidades, color='#1f77b4', alpha=0.1)
    plt.xticks(rotation=45)
    plt.xlabel('Hora (UTC)')
    plt.ylabel('gCO2eq/kWh')
    plt.title(f'Intensidad de carbono por hora en {CODIGO_PAIS}')
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.ylim(180, max(intensidades) + 10)  
    plt.savefig('Grafico_intensidad_carbono.png')
    plt.show()

mezcla_hist = obtener_mezcla_historica(CODIGO_PAIS, API_KEY)

#Grafico mezcla de generación
if mezcla_hist:
    
    breakdown = mezcla_hist[5]['powerProductionBreakdown']
    # Filtramos solo las fuentes con valor numérico 
    fuentes = []
    valores = []
    for fuente, valor in breakdown.items():
        if isinstance(valor, (int, float)) and valor > 0:
            fuentes.append(fuente)
            valores.append(valor)
    total = sum(valores)
    porcentajes = [v * 100 / total for v in valores]

    plt.figure(figsize=(7,7))
    plt.pie(porcentajes, labels=fuentes, autopct='%1.1f%%', startangle=140)
    plt.title(f'Mezcla de generación eléctrica en {CODIGO_PAIS}\n({mezcla_hist[0]["datetime"][:10]})')
    plt.axis('equal')
    plt.savefig('Grafico_mezcla_generacion.png')
    plt.show()
else:
    print("No se pudo obtener la mezcla histórica.")

    