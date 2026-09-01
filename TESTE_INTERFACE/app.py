from flask import Flask, jsonify, render_template
import serial
import threading
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

# Configuração da porta serial
ser = None


def init_serial():
    global ser
    try:
        ser = serial.Serial('COM5', 9600)
        print("Porta COM5 aberta com sucesso!")
    except serial.SerialException as e:
        print(f"Erro ao abrir a porta serial: {e}")
        ser = None


data = {
    "ldr": 0,
    "led": "Desligado",
    "temperature": 0,
    "buzzer": "Desligado",
    "water_level": 0,
    "pump": "Desligado",
    "situation": 0
}


def determine_situation():
    ldr = data["ldr"]
    temperature = data["temperature"]
    water_level = data["water_level"]

    luminosity = "Baixa" if ldr < 600 else "Alta"
    temp_status = "Normal" if temperature <= 30 else "Alta"
    water_status = "Baixo" if water_level == 0 else "Alto"

    if luminosity == "Baixa" and temp_status == "Normal" and water_status == "Alto":
        return 1
    elif luminosity == "Baixa" and temp_status == "Normal" and water_status == "Baixo":
        return 2
    elif luminosity == "Baixa" and temp_status == "Alta" and water_status == "Alto":
        return 3
    elif luminosity == "Baixa" and temp_status == "Alta" and water_status == "Baixo":
        return 4
    elif luminosity == "Alta" and temp_status == "Normal" and water_status == "Alto":
        return 5
    elif luminosity == "Alta" and temp_status == "Normal" and water_status == "Baixo":
        return 6
    elif luminosity == "Alta" and temp_status == "Alta" and water_status == "Alto":
        return 7
    elif luminosity == "Alta" and temp_status == "Alta" and water_status == "Baixo":
        return 8
    return 0


def read_from_serial():
    if ser:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                # Adiciona uma linha de depuração
                print(f"Received line: {line}")
                parts = line.split(", ")
                for part in parts:
                    if "LDR: " in part:
                        data["ldr"] = int(part.split(": ")[1])
                    elif "LED: " in part:
                        data["led"] = part.split(": ")[1]
                    elif "Temp: " in part:
                        data["temperature"] = float(part.split(": ")[1])
                    elif "Buzzer: " in part:
                        data["buzzer"] = part.split(": ")[1]
                    elif "Water Level: " in part:
                        data["water_level"] = int(part.split(": ")[1])
                    elif "Bomba: " in part:
                        data["pump"] = part.split(": ")[1]

                data["situation"] = determine_situation()
                store_data_in_db()
                store_alarm_if_needed()
                remove_old_data()


def store_data_in_db():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                 (timestamp TEXT, ldr INTEGER, led TEXT, temperature REAL, buzzer TEXT, water_level INTEGER, pump TEXT, situation INTEGER)''')
    c.execute("INSERT INTO sensor_data VALUES (?,?,?,?,?,?,?,?)",
              (datetime.now(), data["ldr"], data["led"], data["temperature"], data["buzzer"], data["water_level"], data["pump"], data["situation"]))
    conn.commit()
    conn.close()


def store_alarm_if_needed():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alarms
                 (timestamp TEXT, message TEXT)''')

    if data["led"] == "Ligado" and data["ldr"] < 600:
        c.execute("INSERT INTO alarms VALUES (?,?)",
                  (datetime.now(), "Luminosidade baixa: LED aceso"))
    if data["buzzer"] == "Ligado" and data["temperature"] > 30:
        c.execute("INSERT INTO alarms VALUES (?,?)",
                  (datetime.now(), "Temperatura alta: Buzzer acionado"))
    if data["pump"] == "Ligado" and data["water_level"] == 0:
        c.execute("INSERT INTO alarms VALUES (?,?)",
                  (datetime.now(), "Nível de água baixo: Bomba acionada"))

    conn.commit()
    conn.close()


def remove_old_data():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    time_threshold = datetime.now() - timedelta(seconds=60)
    c.execute("DELETE FROM sensor_data WHERE timestamp < ?", (time_threshold,))
    c.execute("DELETE FROM alarms WHERE timestamp < ?", (time_threshold,))
    conn.commit()
    conn.close()


def send_email(subject, body, attachment=None):
    # Altere para seu email
    sender_email = ""
    receiver_email = ""
    password = ""

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename= {attachment.name}')
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email enviado com sucesso")
    except Exception as e:
        print(f"Erro ao enviar email: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data)


@app.route('/report')
def generate_report():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_data")
    rows = c.fetchall()
    conn.close()

    # Criar conteúdo do relatório
    report_content = "Timestamp, LDR, LED, Temperature, Buzzer, Water Level, Pump, Situation\n"
    for row in rows:
        report_content += ", ".join(map(str, row)) + "\n"

    # Enviar email com o relatório
    report_file = io.StringIO(report_content)
    report_file.name = 'report.csv'
    send_email("Relatório de Dados",
               "Segue em anexo o relatório de dados dos sensores.", report_file)

    return render_template('report.html', rows=rows)


@app.route('/graph_report')
def graph_report():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, ldr, temperature, water_level FROM sensor_data")
    rows = c.fetchall()
    conn.close()

    timestamps = [datetime.strptime(
        row[0], "%Y-%m-%d %H:%M:%S.%f") for row in rows]
    ldr_values = [row[1] for row in rows]
    temperature_values = [row[2] for row in rows]
    water_level_values = [row[3] for row in rows]

    fig, axs = plt.subplots(3, 1, figsize=(10, 15))

    date_str = timestamps[0].strftime('%Y-%m-%d')

    axs[0].plot(timestamps, ldr_values, label='LDR')
    axs[0].set_title(f'LDR Values Over Time ({date_str})')
    axs[0].set_xlabel('Timestamp')
    axs[0].set_ylabel('LDR')
    axs[0].legend()
    axs[0].xaxis.set_major_formatter(
        plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    # Limitar o número de valores no eixo x
    axs[0].xaxis.set_major_locator(plt.MaxNLocator(10))

    axs[1].plot(timestamps, temperature_values, label='Temperature', color='r')
    axs[1].set_title(f'Temperature Over Time ({date_str})')
    axs[1].set_xlabel('Timestamp')
    axs[1].set_ylabel('Temperature (°C)')
    axs[1].legend()
    axs[1].xaxis.set_major_formatter(
        plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    # Limitar o número de valores no eixo x
    axs[1].xaxis.set_major_locator(plt.MaxNLocator(10))

    axs[2].plot(timestamps, water_level_values, label='Water Level', color='b')
    axs[2].set_title(f'Water Level Over Time ({date_str})')
    axs[2].set_xlabel('Timestamp')
    axs[2].set_ylabel('Water Level')
    axs[2].legend()
    axs[2].xaxis.set_major_formatter(
        plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    # Limitar o número de valores no eixo x
    axs[2].xaxis.set_major_locator(plt.MaxNLocator(10))

    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    # Enviar email com o gráfico
    img.seek(0)
    img.name = 'report.png'
    send_email("Relatório de Gráficos",
               "Segue em anexo o relatório de gráficos.", img)

    return render_template('graph_report.html', graph_url=graph_url)


@app.route('/alarm_report')
def alarm_report():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM alarms")
    rows = c.fetchall()
    conn.close()

    # Criar conteúdo do relatório de alarmes
    alarm_content = "Timestamp, Message\n"
    for row in rows:
        alarm_content += f"{row[0]}, {row[1]}\n"

    # Enviar email com o relatório de alarmes
    alarm_file = io.StringIO(alarm_content)
    alarm_file.name = 'alarm_report.csv'
    send_email("Relatório de Alarmes",
               "Segue em anexo o relatório de alarmes.", alarm_file)

    return render_template('alarm_report.html', rows=rows)


if __name__ == '__main__':
    init_serial()
    if ser:
        threading.Thread(target=read_from_serial, daemon=True).start()
    app.run(host='0.0.0.0')
