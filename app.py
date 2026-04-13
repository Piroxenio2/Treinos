import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Treino Tracker Pro", page_icon="💪", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Certifique-se de que no Streamlit Cloud você configurou os "Secrets"
conn = st.connection("gsheets", type=GSheetsConnection)

# NOME DA ABA (Mude aqui se na sua planilha estiver diferente de 'Página1')
NOME_ABA = "Página1"

def carregar_dados():
    try:
        # Lê os dados da planilha. ttl="0s" força a buscar dados novos sempre.
        df = conn.read(worksheet=NOME_ABA, ttl="0s")
        if df.empty or "Data_Hora" not in df.columns:
            return pd.DataFrame(columns=["Data_Hora", "Exercicio", "Peso_kg", "Repeticoes", "Series", "Volume_Total"])
        return df
    except Exception as e:
        # Se der erro (ex: aba não existe), retorna estrutura vazia para não quebrar o app
        return pd.DataFrame(columns=["Data_Hora", "Exercicio", "Peso_kg", "Repeticoes", "Series", "Volume_Total"])

# Lista Completa de Exercícios
LISTA_EXERCICIOS = [
    "Outro...", "Supino Reto (Barra)", "Supino Reto (Halter)", "Supino Inclinado (Halter)", 
    "Supino Inclinado (Máquina)", "Crossover (Polia)", "Peck Deck / Voador", "Flexão de Braços", 
    "Crucifixo (Máquina)", "Supino Vertical", "Crucifixo", "Puxada Alta (Frente)", "Barra Fixa", 
    "Remada Baixa (Barra)", "Remada Baixa (Triângulo)", "Remada Curvada", "Remada Articulada (Máquina)", 
    "Pulldown", "Remada Serrote", "Encolhimento", "Desenvolvimento (Halter)", "Desenvolvimento (Máquina)", 
    "Elevação Frontal", "Elevação Lateral", "Elevação Lateral (Polia)", "Crucifixo Inverso", "Remada Alta",
    "Agachamento Livre", "Leg Press 45", "Cadeira Extensora", "Mesa Flexora", "Stiff", "Afundo / Passada", 
    "Panturrilha (Máquina/Leg)", "Bulgaro", "Elevação Pélvica", "Agachamento (Halteres)", "Tríceps Corda", 
    "Tríceps Testa", "Tríceps Testa Máquina", "Tríceps Coice", "Rosca Direta", "Rosca Inclinada", 
    "Rosca Martelo", "Rosca Tríceps", "Flexão de Punho", "Rosca Inversa", "Abdominal Máquina", 
    "Abdominal Infra (Paralela)", "Abdominal Supra (Solo)"
]

def traduzir_dia(data):
    dias = {'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
            'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    return dias.get(data.strftime('%A'), data.strftime('%A'))

# --- TÍTULO ---
st.title("🏋️ Monitor de Treino - Academia")

aba_registro, aba_historico, aba_graficos, aba_fichas = st.tabs([
    "📝 Novo Treino", "📅 Últimos 10 Treinos", "📈 Gráficos", "📋 Fichas de Treino"
])

# ===================================================
# ABA 1: REGISTRO
# ===================================================
with aba_registro:
    st.write("Preencha o exercício feito:")
    
    with st.form("form_treino", clear_on_submit=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            data_input = st.date_input("Data", datetime.now())
            hora_input = st.time_input("Hora", datetime.now().time())
        with c2:
            escolha = st.selectbox("Exercício", LISTA_EXERCICIOS)
            nome_outro = st.text_input("Se for 'Outro...', digite aqui:")

        st.markdown("---")
        c3, c4, c5 = st.columns(3)
        with c3:
            peso = st.number_input("Carga (kg)", min_value=0.0, step=0.5)
        with c4:
            reps = st.number_input("Repetições", min_value=0, step=1)
        with c5:
            series = st.number_input("Séries", min_value=1, step=1, value=3)
            
        enviado = st.form_submit_button("💾 Salvar no Google Sheets", type="primary")

    if enviado:
        nome_final = nome_outro if escolha == "Outro..." else escolha
        if not nome_final:
            st.error("Erro: Escolha um nome para o exercício.")
        else:
            try:
                # 1. Busca dados atuais
                df_antigo = carregar_dados()
                
                # 2. Cria o novo registro
                data_combinada = datetime.combine(data_input, hora_input)
                novo_registro = {
                    "Data_Hora": data_combinada.strftime('%Y-%m-%d %H:%M:%S'),
                    "Exercicio": nome_final,
                    "Peso_kg": float(peso),
                    "Repeticoes": int(reps),
                    "Series": int(series),
                    "Volume_Total": float(peso * reps * series)
                }
                
                # 3. Une e atualiza
                df_novo = pd.concat([df_antigo, pd.DataFrame([novo_registro])], ignore_index=True)
                conn.update(worksheet=NOME_ABA, data=df_novo)
                
                st.success(f"✅ {nome_final} sincronizado!")
                st.balloons()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# ===================================================
# ABA 2: HISTÓRICO
# ===================================================
with aba_historico:
    df = carregar_dados()
    if not df.empty and "Data_Hora" in df.columns:
        df['Data_Hora'] = pd.to_datetime(df['Data_Hora'])
        df['Data_Simples'] = df['Data_Hora'].dt.date
        dias_unicos = sorted(df['Data_Simples'].unique(), reverse=True)[:10]
        
        if not dias_unicos:
            st.info("Nenhum treino encontrado.")
        else:
            abas = st.tabs([f"{traduzir_dia(d)} ({d.strftime('%d/%m')})" for d in dias_unicos])
            for i, aba in enumerate(abas):
                with aba:
                    df_dia = df[df['Data_Simples'] == dias_unicos[i]].sort_values(by="Data_Hora")
                    st.dataframe(df_dia[['Exercicio', 'Peso_kg', 'Repeticoes', 'Series']], use_container_width=True, hide_index=True)
                    st.caption(f"Volume Total: {df_dia['Volume_Total'].sum():,.0f} kg")
    else:
        st.info("O histórico aparecerá aqui após o primeiro registro.")

# ===================================================
# ABA 3: GRÁFICOS
# ===================================================
with aba_graficos:
    df = carregar_dados()
    if not df.empty and len(df) > 1:
        lista_ex = sorted(df['Exercicio'].unique())
        opcao = st.selectbox("Qual exercício quer analisar?", lista_ex)
        df_filt = df[df['Exercicio'] == opcao].sort_values(by="Data_Hora")
        st.line_chart(df_filt, x="Data_Hora", y="Peso_kg")
        st.metric("Recorde Pessoal (PR)", f"{df_filt['Peso_kg'].max()} kg")
    else:
        st.warning("Dados insuficientes para gerar gráficos.")

# ===================================================
# ABA 4: FICHAS (CONTEÚDO ESTÁTICO)
# ===================================================
with aba_fichas:
    st.header("📚 Suas Fichas")
    with st.expander("TREINO A - Empurrar"):
        st.markdown("- [ ] Supino Vertical\n- [ ] Supino Reto\n- [ ] Desenvolvimento\n- [ ] Elevação Lateral")
    with st.expander("TREINO B - Pernas"):
        st.markdown("- [ ] Agachamento\n- [ ] Stiff\n- [ ] Extensora\n- [ ] Panturrilha")
    with st.expander("TREINO C - Puxar"):
        st.markdown("- [ ] Puxada Alta\n- [ ] Remada Baixa\n- [ ] Rosca Direta\n- [ ] Rosca Martelo")
