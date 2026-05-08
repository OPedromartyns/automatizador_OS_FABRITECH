from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os
from dotenv import load_dotenv

import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar

load_dotenv()

USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
URL = os.getenv("URL")
DIAS_PRESENCIAIS = tuple(map(int, os.getenv("DIAS_PRESENCIAIS").split(",")))

# Seleção manual da data para lançamento
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
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    cal = Calendar(
        janela,
        selectmode='day',
        date_pattern='dd/mm/yyyy'
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


# Preenche um item da OS (turno/intervalo)
def preencher_item(driver, wait, num, inicio, fim, desc):

    Select(wait.until(
        EC.presence_of_element_located(
            (By.NAME, f"tipo_tarefa_{num:03d}")
        )
    )).select_by_value("SUP")

    Select(wait.until(
        EC.presence_of_element_located(
            (By.NAME, f"modulo_{num:03d}")
        )
    )).select_by_value("COM")

    driver.execute_script(
        "arguments[0].value = arguments[1];",
        wait.until(EC.presence_of_element_located(
            (By.NAME, f"hora_inicial_{num:03d}")
        )),
        inicio
    )

    driver.execute_script(
        "arguments[0].value = arguments[1];",
        wait.until(EC.presence_of_element_located(
            (By.NAME, f"hora_final_{num:03d}")
        )),
        fim
    )

    driver.execute_script(
        "arguments[0].value = arguments[1];",
        wait.until(EC.presence_of_element_located(
            (By.NAME, f"descricao_{num:03d}")
        )),
        desc
    )


def rodar_automacao():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option(
        'excludeSwitches',
        ['enable-logging']
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    wait = WebDriverWait(driver, 15)

    try:
        # Login inicial
        driver.get(URL)
        driver.maximize_window()

        wait.until(
            EC.presence_of_element_located(
                (By.ID, "id_username")
            )
        ).send_keys(USUARIO)

        wait.until(
            EC.presence_of_element_located(
                (By.ID, "id_password")
            )
        ).send_keys(SENHA)

        wait.until(
            EC.element_to_be_clickable(
                (By.ID, "loginBtn")
            )
        ).click()

        xpath_menu_agendas = "/html/body/main/div/aside/nav/div[1]/a"

        # Loop contínuo para múltiplos lançamentos
        while True:
            entrada = escolher_data()

            if entrada is None:
                print("Encerrado pelo usuário.")
                break

            # Garante retorno à tela principal
            if "agendas" not in driver.current_url.lower():
                botao_agendas = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, xpath_menu_agendas)
                    )
                )
                driver.execute_script(
                    "arguments[0].click();",
                    botao_agendas
                )

            hoje = datetime.strptime(
                entrada,
                "%d/%m/%Y"
            ).strftime("%Y-%m-%d")

            # Aplica filtro por data
            for campo_id in ["data_inicio", "data_fim"]:
                campo = wait.until(
                    EC.presence_of_element_located(
                        (By.ID, campo_id)
                    )
                )

                driver.execute_script(
                    "arguments[0].value = arguments[1];",
                    campo,
                    hoje
                )

            # Busca agenda
            botao_buscar = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="form-filtro-agendas"]/div[2]/div[3]/button'
                    )
                )
            )
            driver.execute_script(
                "arguments[0].click();",
                botao_buscar
            )

            # Abre lançamento
            botao_acoes = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class,'btn-actions')]")
                )
            )
            driver.execute_script(
                "arguments[0].click();",
                botao_acoes
            )

            botao_lancar = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[contains(@class,'dropdown-menu')]//button[@type='submit']"
                    )
                )
            )
            driver.execute_script(
                "arguments[0].click();",
                botao_lancar
            )

            # Horário padrão da OS
            driver.execute_script(
                "arguments[0].value = '08:00';",
                wait.until(EC.visibility_of_element_located(
                    (By.ID, "hora_inicio_os")
                ))
            )

            driver.execute_script(
                "arguments[0].value = '18:00';",
                wait.until(EC.visibility_of_element_located(
                    (By.ID, "hora_fim_os")
                ))
            )

            # Segunda e quinta = presencial | demais = remoto
            campo_data = wait.until(
                EC.presence_of_element_located(
                    (By.NAME, "data_os")
                )
            )

            data_obj = datetime.strptime(
                campo_data.get_attribute("value"),
                "%d/%m/%Y"
            )

            tipo = "P" if data_obj.weekday() in DIAS_PRESENCIAIS else "R"

            Select(wait.until(
                EC.presence_of_element_located(
                    (By.NAME, "tipo_atendimento_os")
                )
            )).select_by_value(tipo)

            # Estrutura padrão dos itens
            preencher_item(driver, wait, 1, "08:00", "12:00", "primeiro turno")

            wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "btn-add-item")
                )
            ).click()

            preencher_item(driver, wait, 2, "12:00", "13:00", "Intervalo")

            wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "btn-add-item")
                )
            ).click()

            preencher_item(driver, wait, 3, "13:00", "18:00", "segundo turno")

            # Finaliza lançamento
            botao_salvar = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "btn-salvar-lancamento")
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                botao_salvar
            )

            print(
                f"OS lançada para {entrada} | "
                f"{'Presencial' if tipo == 'P' else 'Remoto'}"
            )

            time.sleep(3)

    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    rodar_automacao()
    # by Pedro H Martins