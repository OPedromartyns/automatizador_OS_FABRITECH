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
DIAS_PRESENCIAIS = tuple(map(int, os.getenv("DIAS_PRESENCIAIS").split(",")))



# ==========================
# CALENDARIO
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

    tk.Label(
        janela,
        text="Selecionar OS",
        font=("Arial",14,"bold")
    ).pack(pady=10)


    cal = Calendar(
        janela,
        selectmode="day",
        date_pattern="dd/mm/yyyy"
    )

    cal.pack(pady=20)


    ttk.Button(
        janela,
        text="Lançar OS",
        command=pegar_data
    ).pack()

    janela.protocol("WM_DELETE_WINDOW", fechar)
    janela.mainloop()


    return data_escolhida[0] if data_escolhida else None




# ==========================
# ITEM OS
# ==========================

def preencher_item(driver, wait, num, inicio, fim, desc):


    Select(wait.until(
        EC.presence_of_element_located(
            (By.NAME,f"tipo_tarefa_{num:03d}")
        )
    )).select_by_value("SUP")


    Select(wait.until(
        EC.presence_of_element_located(
            (By.NAME,f"modulo_{num:03d}")
        )
    )).select_by_value("COM")



    driver.execute_script(
        "arguments[0].value=arguments[1]",
        wait.until(
            EC.presence_of_element_located(
                (By.NAME,f"hora_inicial_{num:03d}")
            )
        ),
        inicio
    )


    driver.execute_script(
        "arguments[0].value=arguments[1]",
        wait.until(
            EC.presence_of_element_located(
                (By.NAME,f"hora_final_{num:03d}")
            )
        ),
        fim
    )


    driver.execute_script(
        "arguments[0].value=arguments[1]",
        wait.until(
            EC.presence_of_element_located(
                (By.NAME,f"descricao_{num:03d}")
            )
        ),
        desc
    )





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
        wait.until(
            EC.presence_of_element_located(
                (By.ID,"id_username")
            )
        ).send_keys(USUARIO)

        wait.until(
            EC.presence_of_element_located(
                (By.ID,"id_password")
            )
        ).send_keys(SENHA)

        wait.until(
            EC.element_to_be_clickable(
                (By.ID,"loginBtn")
            )
        ).click()

        print("[2] Login OK")


        # OPERACIONAL
        operacional = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,"a.quick-card.operacional")
            )
        )
        operacional.click()

        print("[3] Operacional aberto")


        # ======================
        # LOOP DE LANÇAMENTOS
        # ======================
        while True:

            # DATA MANUAL
            entrada = escolher_data()

            if entrada is None:
                print("Encerrado pelo usuário (Calendário fechado ou cancelado).")
                break

            print(f"[5] Data escolhida {entrada}")

            # Garante que voltou para a tela de agendas se tiver saído dela no loop anterior
            if "agendas" not in driver.current_url.lower():
                # Se o sistema não voltar sozinho após salvar, força a volta clicando no menu lateral/card correspondente
                # (Ajuste o seletor abaixo se houver um botão de voltar ou menu lateral específico)
                driver.get(URL) # Uma alternativa segura é recarregar a URL base ou ir direto para a página de filtros
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"a.quick-card.operacional"))).click()

            # CLIENTE
            campo_cliente = wait.until(
                EC.element_to_be_clickable(
                    (
                    By.CSS_SELECTOR,
                    "#form-filtro-agendas > div:nth-child(2) > div > span > span.selection > span > span > textarea"
                    )
                )
            )
            campo_cliente.send_keys("FABRITECH")
            campo_cliente.send_keys(Keys.ENTER)

            print("[4] Cliente selecionado")


            hoje = datetime.strptime(
                entrada,
                "%d/%m/%Y"
            ).strftime("%Y-%m-%d")


            # FILTRO DATA
            for campo_id in ["data_inicio","data_fim"]:

                campo = wait.until(
                    EC.presence_of_element_located(
                        (By.ID,campo_id)
                    )
                )

                driver.execute_script(
                    "arguments[0].value=arguments[1]",
                    campo,
                    hoje
                )

            print("[6] Data aplicada")


            # BUSCAR
            botao_buscar = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "#form-filtro-agendas > div.filter-row.filter-dates > div.search-button > button"
                    )
                )
            )
            driver.execute_script(
                "arguments[0].click();",
                botao_buscar
            )

            print("[7] Agenda pesquisada")


            # AÇÕES
            wait.until(
                EC.element_to_be_clickable(
                    (
                    By.XPATH,
                    "//button[contains(@class,'btn-actions')]"
                    )
                )
            ).click()


            wait.until(
                EC.element_to_be_clickable(
                    (
                    By.XPATH,
                    "//div[contains(@class,'dropdown-menu')]//button[@type='submit']"
                    )
                )
            ).click()

            print("[8] Lancamento aberto")


            # HORARIOS
            driver.execute_script(
                "arguments[0].value='08:00'",
                wait.until(
                    EC.visibility_of_element_located(
                        (By.ID,"hora_inicio_os")
                    )
                )
            )

            driver.execute_script(
                "arguments[0].value='18:00'",
                wait.until(
                    EC.visibility_of_element_located(
                        (By.ID,"hora_fim_os")
                    )
                )
            )


            # TIPO
            campo_data = wait.until(
                EC.presence_of_element_located(
                    (By.NAME,"data_os")
                )
            )

            data_obj = datetime.strptime(
                campo_data.get_attribute("value"),
                "%d/%m/%Y"
            )

            tipo = "P" if data_obj.weekday() in DIAS_PRESENCIAIS else "R"

            Select(
                wait.until(
                    EC.presence_of_element_located(
                        (By.NAME,"tipo_atendimento_os")
                    )
                )
            ).select_by_value(tipo)


            # ITENS
            preencher_item(
                driver,wait,
                1,
                "08:00",
                "12:00",
                "primeiro turno"
            )

            wait.until(
                EC.element_to_be_clickable(
                    (By.ID,"btn-add-item")
                )
            ).click()

            preencher_item(
                driver,wait,
                2,
                "12:00",
                "13:00",
                "Intervalo"
            )

            wait.until(
                EC.element_to_be_clickable(
                    (By.ID,"btn-add-item")
                )
            ).click()

            preencher_item(
                driver,wait,
                3,
                "13:00",
                "18:00",
                "segundo turno"
            )


            # SALVAR
            wait.until(
                EC.element_to_be_clickable(
                    (By.ID,"btn-salvar-lancamento")
                )
            ).click()

            print(f"OS lancada {entrada} | {'Presencial' if tipo == 'P' else 'Remoto'}")
            
            # Pequena pausa para o sistema processar antes de abrir o calendário novamente
            time.sleep(3)

    except Exception as e:
        print(f"Erro durante a execução: {e}")


if __name__=="__main__":
    rodar_automacao()