# 📌 Automatizador de Lançamento de OS

## 📖 Objetivo

Esta automação realiza automaticamente o lançamento de Ordens de Serviço (OS) no sistema Agenda.

Foi desenvolvida para:

- Reduzir lançamentos manuais
- Padronizar preenchimentos
- Facilitar manutenção futura
- Permitir configuração sem alterar o código

---

## ⚙️ Funcionalidades

A automação:

✅ Realiza login automaticamente  
✅ Exibe calendário para seleção manual da data  
✅ Busca a agenda da data selecionada  
✅ Define atendimento presencial/remoto automaticamente  
✅ Preenche os horários padrão  
✅ Salva o lançamento  
✅ Permite múltiplos lançamentos na mesma sessão

---

## 📂 Estrutura do Projeto

```bash
AUTOMATIZADOR_OS/
│
├── .env
├── .gitignore
├── LANCADOR_DE_OS.py
├── requirements.txt
├── README.md
├── icone.ico
│
├── build/
└── dist/
```

---

## 🛠 Requisitos

Antes de utilizar:

- Python 3.14+
- Visual Studio Code
- Google Chrome
- Internet ativa

---

## 📥 Instalação das Dependências

No terminal do VS Code:

```bash
pip install -r requirements.txt
```

Se necessário:

```bash
pip install selenium webdriver-manager python-dotenv tkcalendar pyinstaller
```

---

## 🔐 Configuração de Credenciais

A automação utiliza um arquivo `.env`.

Criar na raiz do projeto:

```bash
.env
```

Conteúdo:

```env
USUARIO=SEU_LOGIN
SENHA=SUA_SENHA
URL=https://agenda.fabritech.com.br/login/
DIAS_PRESENCIAIS=0,3
```

---

## Alteração de Usuário

Editar:

```env
USUARIO=
```

Exemplo:

```env
USUARIO=joao.silva
```

---

## Alteração de Senha

Editar:

```env
SENHA=
```

Exemplo:

```env
SENHA=Senha@123
```

---

## ⚠️ Boas práticas

Nunca colocar usuário e senha diretamente no código.

✅ Correto:

```env
USUARIO=joao.silva
SENHA=Senha@123
```

❌ Incorreto:

```python
send_keys("joao.silva")
send_keys("Senha@123")
```

---

## 📅 Configuração dos Dias Presenciais

A definição é feita no `.env`.

Editar:

```env
DIAS_PRESENCIAIS=
```

---

### Tabela de referência

| Dia | Número |
|-----|--------|
| Segunda | 0 |
| Terça | 1 |
| Quarta | 2 |
| Quinta | 3 |
| Sexta | 4 |
| Sábado | 5 |
| Domingo | 6 |

---

### Configuração atual

```env
DIAS_PRESENCIAIS=0,3
```

Resultado:

- Segunda → Presencial
- Quinta → Presencial
- Demais dias → Remoto

---

### Exemplos

#### Terça e quinta

```env
DIAS_PRESENCIAIS=1,3
```

#### Apenas quarta

```env
DIAS_PRESENCIAIS=2
```

#### Segunda, quarta e sexta

```env
DIAS_PRESENCIAIS=0,2,4
```

---

## ▶️ Executar no VS Code

No terminal:

```bash
python LANCADOR_DE_OS.py
```

---

## 🖥 Fluxo de Execução

Ao iniciar:

### 1. Login automático

A automação acessa o sistema usando o `.env`

### 2. Seleção de data

Abre o calendário

### 3. Busca agenda

Filtra pela data selecionada

### 4. Preenchimento automático

| Item | Horário | Descrição |
|------|---------|-----------|
| 1 | 08:00 às 12:00 | primeiro turno |
| 2 | 12:00 às 13:00 | Intervalo |
| 3 | 13:00 às 18:00 | segundo turno |

### 5. Salvamento

Finaliza automaticamente

---

## ⚙️ Gerar Executável (.exe)

Sempre que houver alteração no código ou estrutura:

```bash
pyinstaller --onefile --windowed --icon=icone.ico LANCADOR_DE_OS.py
```

---

## 📂 Local do Executável

Após gerar:

```bash
dist/
```

Arquivo:

```bash
LANCADOR_DE_OS.exe
```

---

## 🔄 Sempre que Alterar

Se modificar:

- Código
- Dependências
- Estrutura
- Ícone

Excluir:

```bash
build/
dist/
LANCADOR_DE_OS.spec
```

Depois gerar novamente.

---

## 🧪 Teste Obrigatório

Após gerar o executável, validar:

- ✅ Login realizado
- ✅ Calendário abriu
- ✅ Busca agenda
- ✅ Preenchimento correto
- ✅ Salvamento executado

---

## ❌ Solução de Problemas

### Chrome não abre

```bash
pip install --upgrade webdriver-manager selenium
```

---

### Erro de login

Verificar `.env`

- usuário
- senha
- URL

---

### Calendário não abre

```bash
pip install tkcalendar
```

---

### Executável fecha sozinho

Executar pelo terminal:

```bash
dist\LANCADOR_DE_OS.exe
```

---

## 🔧 Manutenção Técnica

Se a automação parar sem alterações locais, provavelmente houve mudança no sistema Agenda.

Pode exigir ajuste em:

- `By.ID`
- `By.XPATH`
- `By.NAME`

Ou mudanças estruturais da página.

---

## 🚀 Melhorias Futuras

- Arquivo de log
- Histórico de lançamentos
- Tela para editar configurações
- Validação automática de erro
- Tela de configuração integrada
- Indicador visual de sucesso/falha

---

## 👨‍💻 Autor

**Pedro H Martins**