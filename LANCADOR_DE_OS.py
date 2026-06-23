from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar

import time
import os
from dotenv import load_dotenv

load_dotenv()

USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
URL = os.getenv("URL")

# Tratamento preventivo caso a variável venha vazia ou com espaços
DIAS_STR = os.getenv("DIAS_PRESENCIAIS", "")
DIAS_PRESENCIAIS = tuple(map(int, DIAS_STR.split(","))) if DIAS_STR else ()

# ==========================
# CALENDÁRIO (UI)
# ==========================
def escolher_data():
    data_escolhida = []

    def pegar_data():
        data_escolhida.append(cal.get_date())
        janela.destroy()

    def fechar():
        janela.destroy()

    janela = tk.Tk()
    janela.title("Selecionar OS")
    janela.geometry("350x350")
    janela.eval('tk::PlaceWindow . center') # Centraliza a janela na tela

    tk.Label(janela, text="Selecionar OS", font=("Arial", 14, "bold")).pack(pady=10)

    cal = Calendar(janela, selectmode="day", date_pattern="dd/mm/yyyy")
    cal.pack(pady=20)

    ttk.Button(janela, text="Lançar OS", command=pegar_data).pack()

    janela.protocol("WM_DELETE_WINDOW", fechar)
    janela.mainloop()

    return data_escolhida[0] if data_escolhida else None


# ==========================
# ITEM DA OS
# ==========================
def preencher_item(driver, wait, num, inicio, fim, desc):
    # Aguarda o elemento estar visível e interativo antes de injetar via JS
    tipo_campo = wait.until(EC.presence_of_element_located((By.NAME, f"tipo_tarefa_{num:03d}")))
    Select(tipo_campo).select_by_value("SUP")

    modulo_campo = wait.until(EC.presence_of_element_located((By.NAME, f"modulo_{num:03d}")))
    Select(modulo_campo).select_by_value("COM")

    hora_ini = wait.until(EC.presence_of_element_located((By.NAME, f"hora_inicial_{num:03d}")))
    driver.execute_script("arguments[0].value=arguments[1];", hora_ini, inicio)

    hora_fim = wait.until(EC.presence_of_element_located((By.NAME, f"hora_final_{num:03d}")))
    driver.execute_script("arguments[0].value=arguments[1];", hora_fim, fim)

    desc_campo = wait.until(EC.presence_of_element_located((By.NAME, f"descricao_{num:03d}")))
    driver.execute_script("arguments[0].value=arguments[1];", desc_campo, desc)


# ==========================
# AUTOMACAO
# ==========================


def rodar_automacao():


    options = Options()

    options.add_experimental_option(
        "detach",
        True
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"]
    )

    # LINHA ADICIONADA AQUI PARA FORÇAR O ZOOM EM 100%:
    options.add_argument("--force-device-scale-factor=1")


    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )


    wait = WebDriverWait(driver,20)

    try:
        driver.get(URL)
        driver.maximize_window()

        print("[1] Pagina aberta")

        # LOGIN
        wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(USUARIO)
        wait.until(EC.presence_of_element_located((By.ID, "id_password"))).send_keys(SENHA)
        wait.until(EC.element_to_be_clickable((By.ID, "loginBtn"))).click()
        print("[2] Login OK")

        # OPERACIONAL (Primeiro acesso)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.quick-card.operacional"))).click()
        print("[3] Operacional aberto")

        # ======================
        # LOOP DE LANÇAMENTOS
        # ======================
        while True:
            entrada = escolher_data()
            if entrada is None:
                print("Encerrado pelo usuário (Calendário fechado ou cancelado).")
                break

            print(f"\n[5] Data escolhida: {entrada}")

            # Retorno seguro para a página operacional se o sistema navegar para longe
            if "agendas" not in driver.current_url.lower():
                driver.get(URL)
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.quick-card.operacional"))).click()
                time.sleep(1)

            # SELEÇÃO DO CLIENTE
            campo_cliente = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "#form-filtro-agendas > div:nth-child(2) > div > span > span.selection > span > span > textarea"
            )))
            campo_cliente.clear() # Limpa resquícios de loops anteriores
            campo_cliente.send_keys("FABRITECH")
            time.sleep(0.5)
            campo_cliente.send_keys(Keys.ENTER)
            print("[4] Cliente selecionado")

            # FORMATAR DATA PARA O FILTRO JS
            hoje = datetime.strptime(entrada, "%d/%m/%Y").strftime("%Y-%m-%d")

            # FILTRO DATA
            for campo_id in ["data_inicio", "data_fim"]:
                campo = wait.until(EC.presence_of_element_located((By.ID, campo_id)))
                driver.execute_script("arguments[0].value=arguments[1];", campo, hoje)
            print("[6] Data aplicada no filtro")

            # BUSCAR
            botao_buscar = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "#form-filtro-agendas > div.filter-row.filter-dates > div.search-button > button"
            )))
            driver.execute_script("arguments[0].click();", botao_buscar)
            print("[7] Agenda pesquisada")

            # AÇÕES & LANÇAMENTO
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-actions')]"))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'dropdown-menu')]//button[@type='submit']"))).click()
            print("[8] Lançamento aberto")

            # HORÁRIOS GERAIS DA OS
            h_inicio_os = wait.until(EC.visibility_of_element_located((By.ID, "hora_inicio_os")))
            driver.execute_script("arguments[0].value='08:00';", h_inicio_os)

            h_fim_os = wait.until(EC.visibility_of_element_located((By.ID, "hora_fim_os")))
            driver.execute_script("arguments[0].value='18:00';", h_fim_os)

            # IDENTIFICAÇÃO DO TIPO (Presencial / Remoto)
            campo_data = wait.until(EC.presence_of_element_located((By.NAME, "data_os")))
            data_obj = datetime.strptime(campo_data.get_attribute("value"), "%d/%m/%Y")
            
            tipo = "P" if data_obj.weekday() in DIAS_PRESENCIAIS else "R"
            
            select_tipo = wait.until(EC.presence_of_element_located((By.NAME, "tipo_atendimento_os")))
            Select(select_tipo).select_by_value(tipo)

            # PREENCHIMENTO DOS ITENS (Com pequenas pausas para garantir a criação do DOM)
            preencher_item(driver, wait, 1, "08:00", "12:00", "primeiro turno")

            wait.until(EC.element_to_be_clickable((By.ID, "btn-add-item"))).click()
            time.sleep(0.3) # Aguarda o DOM renderizar o item 2
            preencher_item(driver, wait, 2, "12:00", "13:00", "Intervalo")

            wait.until(EC.element_to_be_clickable((By.ID, "btn-add-item"))).click()
            time.sleep(0.3) # Aguarda o DOM renderizar o item 3
            preencher_item(driver, wait, 3, "13:00", "18:00", "segundo turno")

            # SALVAR
            wait.until(EC.element_to_be_clickable((By.ID, "btn-salvar-lancamento"))).click()
            print(f"✔️ OS lançada com sucesso: {entrada} | {'Presencial' if tipo == 'P' else 'Remoto'}")
            
            # Aguarda o processamento do backend antes da próxima iteração
            time.sleep(3)

    except Exception as e:
        print(f"\n❌ Erro crítico detectado durante a execução: {e}")

if __name__ == "__main__":
    rodar_automacao()