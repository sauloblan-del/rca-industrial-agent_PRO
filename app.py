import os
import json
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from weasyprint import HTML

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página Streamlit
st.set_page_config(
    page_title="RCA Industrial Agent | 8D Solver",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Assistente de Análise de Causa Raiz (RCA / 8D)")
st.caption("Solução inteligente para gestão de falhas industriais e diagnóstico de processos.")

# Chave de API
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.sidebar.warning("Insira sua chave de API do Gemini para continuar:")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    st.info("Por favor, adicione sua GEMINI_API_KEY na barra lateral ou no arquivo .env para iniciar.")
    st.stop()

client = genai.Client(api_key=api_key)

# Instração do Agente Conversacional
SYSTEM_INSTRUCTION = """
Você é um Agente Especialista em Resolução de Problemas Industriais (8D e Causa Raiz/RCA).
Sua missão é guiar o usuário de forma metódica e profissional na investigação de falhas de manufatura.

Instruções de Comportamento:
1. Receba o relato do sintoma informado pelo operador ou engenheiro.
2. Aplique a metodologia dos 5 Porquês de forma sequencial, uma pergunta por vez para manter a investigação focada.
3. Avalie as 6 categorias do Diagrama de Ishikawa (Máquina, Mão de Obra, Material, Método, Meio Ambiente, Medição) quando aplicável.
4. Peça confirmações práticas e dados concretos (ex: "Foi verificado se o torque do equipamento mudou?", "Existe medição CMM?").
5. Não aceite causas raízes genéricas como "erro humano" sem aprofundar até encontrar falhas de processo, treinamento ou instrução.
6. Quando a causa raiz for identificada e confirmada pelo usuário, apresente um resumo estruturado no formato 8D e informe que o relatório PDF pode ser baixado na barra lateral.
"""

# Função para gerar o HTML e converter para PDF via WeasyPrint
def generate_8d_pdf(data_8d):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório 8D - Resolução de Problemas Industriais</title>
        <style>
            @page {{
                size: A4;
                margin: 15mm 12mm;
                background-color: #ffffff;
            }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #222222;
                margin: 0;
                padding: 0;
            }}
            *, *::before, *::after {{
                box-sizing: border-box;
            }}
            .header {{
                background-color: #1a365d;
                color: #ffffff;
                padding: 16px 20px;
                margin: -15mm -12mm 15px -12mm;
            }}
            .header h1 {{
                margin: 0;
                font-size: 18pt;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            .header p {{
                margin: 4px 0 0 0;
                font-size: 9pt;
                color: #e2e8f0;
            }}
            .meta-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}
            .meta-table td {{
                padding: 6px 8px;
                border: 1px solid #cbd5e1;
                font-size: 9pt;
                background-color: #f8fafc;
            }}
            .meta-table td.label {{
                font-weight: bold;
                color: #334155;
                width: 20%;
                background-color: #f1f5f9;
            }}
            .section-title {{
                font-size: 11pt;
                font-weight: bold;
                color: #1e3a8a;
                border-left: 4px solid #2563eb;
                padding-left: 8px;
                margin-top: 15px;
                margin-bottom: 8px;
                text-transform: uppercase;
            }}
            .step-box {{
                border: 1px solid #cbd5e1;
                background-color: #ffffff;
                padding: 10px 12px;
                margin-bottom: 12px;
                border-radius: 4px;
                page-break-inside: avoid;
            }}
            .step-header {{
                font-weight: bold;
                color: #0f172a;
                font-size: 10pt;
                margin-bottom: 6px;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 4px;
            }}
            .step-content {{
                font-size: 9.5pt;
                line-height: 1.4;
                color: #334155;
            }}
            ul {{
                margin: 4px 0;
                padding-left: 18px;
            }}
            li {{
                margin-bottom: 3px;
            }}
            .footer {{
                margin-top: 20px;
                border-top: 1px solid #cbd5e1;
                padding-top: 8px;
                font-size: 8pt;
                color: #64748b;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RELATÓRIO 8D — RESOLUÇÃO DE PROBLEMAS</h1>
            <p>RCA Industrial Agent | Diagnóstico de Processo e Causa Raiz</p>
        </div>

        <table class="meta-table">
            <tr>
                <td class="label">ID do Relatório:</td>
                <td>{data_8d.get('id_relatorio', 'RCA-8D-AUTO')}</td>
                <td class="label">Data de Emissão:</td>
                <td>{data_8d.get('data', 'N/A')}</td>
            </tr>
            <tr>
                <td class="label">Área / Linha:</td>
                <td>{data_8d.get('area_linha', 'Manufatura Geral')}</td>
                <td class="label">Especialista:</td>
                <td>Agente RCA AI</td>
            </tr>
        </table>

        <div class="section-title">Detalhamento das Etapas do 8D</div>

        <div class="step-box">
            <div class="step-header">D1 & D2: Formação da Equipe & Descrição do Problema</div>
            <div class="step-content">
                <strong>Descrição da Falha / Sintoma:</strong><br>
                {data_8d.get('d1_d2_descricao', 'Não detalhado.')}
            </div>
        </div>

        <div class="step-box">
            <div class="step-header">D3: Ações de Contenção Imediata</div>
            <div class="step-content">
                {data_8d.get('d3_contencao', 'Nenhuma ação de contenção informada.')}
            </div>
        </div>

        <div class="step-box">
            <div class="step-header">D4: Análise de Causa Raiz (5 Porquês & Ishikawa)</div>
            <div class="step-content">
                <strong>Desdobramento da Causa Raiz:</strong><br>
                {data_8d.get('d4_causa_raiz', 'Análise em andamento.')}
            </div>
        </div>

        <div class="step-box">
            <div class="step-header">D5 & D6: Ações Corretivas Definitivas & Validação</div>
            <div class="step-content">
                {data_8d.get('d5_d6_acoes_corretivas', 'Ações a serem implementadas.')}
            </div>
        </div>

        <div class="step-box">
            <div class="step-header">D7 & D8: Prevenção de Reincidência & Encerramento</div>
            <div class="step-content">
                {data_8d.get('d7_d8_prevencao', 'Padronização de processo pendente.')}
            </div>
        </div>

        <div class="footer">
            Relatório gerado automaticamente por RCA Industrial Agent | Sistema de Gestão de Causa Raiz.
        </div>
    </body>
    </html>
    """
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes

# Inicialização da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Barra lateral para controle e exportação
st.sidebar.header("Painel do Relatório")
if st.session_state.messages:
    if st.sidebar.button("📄 Gerar Relatório 8D em PDF", use_container_width=True):
        with st.spinner("Sintetizando histórico e compilando PDF..."):
            try:
                # Prompt para extrair JSON do histórico
                extraction_prompt = f"""
                Analise o histórico de conversa abaixo e extraia as informações no formato JSON estrito para compor um Relatório 8D.
                Campos obrigatórios no JSON:
                - id_relatorio (String ex: RCA-8D-001)
                - data (String ex: DD/MM/AAAA)
                - area_linha (String)
                - d1_d2_descricao (String)
                - d3_contencao (String)
                - d4_causa_raiz (String)
                - d5_d6_acoes_corretivas (String)
                - d7_d8_prevencao (String)

                Histórico da conversa:
                {json.dumps(st.session_state.messages, ensure_ascii=False)}
                """

                json_res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=extraction_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

                parsed_json = json.loads(json_res.text)
                pdf_data = generate_8d_pdf(parsed_json)

                st.sidebar.download_button(
                    label="⬇️ Baixar PDF do Relatório 8D",
                    data=pdf_data,
                    file_name="Relatorio_8D_RCA.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.sidebar.success("Relatório gerado com sucesso!")
            except Exception as e:
                st.sidebar.error(f"Erro ao gerar PDF: {e}")

# Campo de entrada de mensagem
if user_input := st.chat_input("Descreva o sintoma ou responda à pergunta do agente..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    with st.chat_message("assistant"):
        with st.spinner("Analisando processo..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.2,
                    )
                )
                bot_response = response.text
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            except Exception as e:
                st.error(f"Erro ao comunicar com o agente: {e}")
from fpdf import FPDF

def generate_8d_pdf(data_8d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "RELATÓRIO 8D — RESOLUÇÃO DE PROBLEMAS", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"ID: {data_8d.get('id_relatorio', 'RCA-8D-001')} | Data: {data_8d.get('data', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Seções
    sections = [
        ("D1/D2: Descrição da Falha", data_8d.get('d1_d2_descricao', '')),
        ("D3: Contenção Imediata", data_8d.get('d3_contencao', '')),
        ("D4: Análise de Causa Raiz", data_8d.get('d4_causa_raiz', '')),
        ("D5/D6: Ações Corretivas", data_8d.get('d5_d6_acoes_corretivas', '')),
        ("D7/D8: Prevenção", data_8d.get('d7_d8_prevencao', ''))
    ]

    for title, content in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, content)
        pdf.ln(3)

    return bytes(pdf.output())
