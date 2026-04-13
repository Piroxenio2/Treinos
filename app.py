import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Treino Tracker Pro", page_icon="💪", layout="wide")

ARQUIVO_DADOS = 'historico_treinos.csv'

# Lista Completa de Exercícios
LISTA_EXERCICIOS = [
    "Outro...", 
    # PEITO
    "Supino Reto (Barra)", "Supino Reto (Halter)", "Supino Inclinado (Halter)", 
    "Supino Inclinado (Máquina)", "Crossover (Polia)", "Peck Deck / Voador",
    "Flexão de Braços", "Crucifixo (Máquina)", "Supino Vertical", "Crucifixo", 
    # COSTAS
    "Puxada Alta (Frente)", "Barra Fixa", "Remada Baixa (Barra)", "Remada Baixa (Triângulo)",
    "Remada Curvada", "Remada Articulada (Máquina)", "Pulldown", "Remada Serrote", "Encolhimento", 
    # OMBROS
    "Desenvolvimento (Halter)", "Desenvolvimento (Máquina)", "Elevação Frontal", 
    "Elevação Lateral", "Elevação Lateral (Polia)", "Crucifixo Inverso", "Remada Alta",
    # PERNAS
    "Agachamento Livre", "Leg Press 45", "Cadeira Extensora", 
    "Mesa Flexora", "Stiff", "Afundo / Passada", "Panturrilha (Máquina/Leg)", "Bulgaro", "Elevação Pélvica", "Agachamento (Halteres)", 
    # BRAÇOS
    "Tríceps Corda", "Tríceps Testa", "Tríceps Testa Máquina", "Tríceps Coice", 
    "Rosca Direta", "Rosca Inclinada", "Rosca Martelo", "Rosca Tríceps", 
    "Flexão de Punho", "Rosca Inversa", 
    # ABDÔMEN
    "Abdominal Máquina", "Abdominal Infra (Paralela)", "Abdominal Supra (Solo)"
]

# --- FUNÇÕES AUXILIARES ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Data_Hora", "Exercicio", "Peso_kg", "Repeticoes", "Series", "Volume_Total"])
    try:
        return pd.read_csv(ARQUIVO_DADOS)
    except:
        return pd.DataFrame(columns=["Data_Hora", "Exercicio", "Peso_kg", "Repeticoes", "Series", "Volume_Total"])

def traduzir_dia(data):
    dias = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    return dias.get(data.strftime('%A'), data.strftime('%A'))

# --- TÍTULO ---
st.title("🏋️ Monitor de Treino - Academia")

# AGORA SÃO 4 ABAS
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
            peso = st.number_input("Carga (kg)", min_value=0.0, step=1.0)
        with c4:
            reps = st.number_input("Repetições", min_value=0, step=1)
        with c5:
            series = st.number_input("Séries", min_value=1, step=1, value=3)
            
        enviado = st.form_submit_button("💾 Salvar Treino", type="primary")

    if enviado:
        nome_final = nome_outro if escolha == "Outro..." else escolha
        
        if not nome_final:
            st.error("Erro: Escolha um nome para o exercício.")
        else:
            try:
                data_combinada = datetime.combine(data_input, hora_input)
                novo = {
                    "Data_Hora": data_combinada,
                    "Exercicio": nome_final,
                    "Peso_kg": peso,
                    "Repeticoes": reps,
                    "Series": series,
                    "Volume_Total": peso * reps * series
                }
                df_antigo = carregar_dados()
                df_novo = pd.concat([df_antigo, pd.DataFrame([novo])], ignore_index=True)
                df_novo.to_csv(ARQUIVO_DADOS, index=False)
                
                st.success(f"✅ {nome_final} registrado!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# ===================================================
# ABA 2: HISTÓRICO INTELIGENTE (10 ÚLTIMOS TREINOS)
# ===================================================
with aba_historico:
    st.header("Seus Últimos 10 Dias de Treino")
    
    df = carregar_dados()
    
    if not df.empty:
        try:
            df['Data_Hora'] = pd.to_datetime(df['Data_Hora'], format='mixed')
            df['Data_Simples'] = df['Data_Hora'].dt.date
            dias_unicos = sorted(df['Data_Simples'].unique(), reverse=True)
            top_dias = dias_unicos[:10] 
            
            if not top_dias:
                st.info("Nenhum treino encontrado.")
            else:
                nomes_abas = [f"{traduzir_dia(d)} ({d.strftime('%d/%m')})" for d in top_dias]
                abas = st.tabs(nomes_abas)
                
                for i, aba in enumerate(abas):
                    with aba:
                        dia_atual = top_dias[i]
                        df_dia = df[df['Data_Simples'] == dia_atual].copy()
                        df_dia = df_dia.sort_values(by="Data_Hora")
                        df_exibir = df_dia[['Exercicio', 'Peso_kg', 'Repeticoes', 'Series']]
                        
                        st.dataframe(df_exibir, use_container_width=True, hide_index=True, height=300)
                        vol_total = df_dia['Volume_Total'].sum()
                        st.caption(f"Volume Total: {vol_total:,.0f} kg")

        except Exception as e:
            st.error(f"Erro ao processar datas: {e}. Tente limpar o arquivo CSV.")
    else:
        st.info("O histórico aparecerá aqui.")

# ===================================================
# ABA 3: GRÁFICOS
# ===================================================
with aba_graficos:
    st.header("Evolução de Carga")
    df = carregar_dados()
    if not df.empty:
        try:
            df['Data_Hora'] = pd.to_datetime(df['Data_Hora'], format='mixed')
            lista_ex = sorted(df['Exercicio'].unique())
            opcao = st.selectbox("Qual exercício quer analisar?", lista_ex)
            
            df_filt = df[df['Exercicio'] == opcao].sort_values(by="Data_Hora")
            
            if not df_filt.empty:
                st.line_chart(df_filt, x="Data_Hora", y="Peso_kg")
                max_carga = df_filt['Peso_kg'].max()
                st.metric("Recorde Pessoal (PR)", f"{max_carga} kg")
            else:
                st.warning("Sem dados.")
        except:
            st.warning("Erro nos dados.")

# ===================================================
# ABA 4: FICHAS DE TREINO (NOVIDADE!)
# ===================================================
with aba_fichas:
    st.header("📚 Suas Fichas de Treino")
    st.markdown("Clique na seta para ver os exercícios do dia.")

    with st.expander("TREINO A - Empurrar (Peito, Ombro, Tríceps, Antebraço)"):
        st.markdown("""
        **1. Peitoral**
        - [ ] Supino Vertical - 4x 12
        - [ ] Supino Reto (Barra) - 4x 8-10
        - [ ] Flexão de Braço - 4x 10-12 / Crucifixo - 4x 10-12
        
        **2. Ombros**
        - [ ] Remada Alta - 3x 8-12
        - [ ] Desenvolvimento Militar - 3x 8-12
        - [ ] Elevação Lateral - 3x 8-12
        
        **3. Tríceps**
        - [ ] Rosca Tríceps - 3x 8-12
        - [ ] Tríceps Testa Máquina - 3x 8-12
        - [ ] Tríceps Coice - 3x 8-12
        
        **4. Antebraço**
        - [ ] Rosca Máquina - 3x 8-12
        """)

    with st.expander("TREINO B - Pernas Completo"):
        st.markdown("""
        **Pernas**
        - [ ] Agachamento Livre - 4x 6-8 (Carga Alta)
        - [ ] Stiff - 4x 8-10
        - [ ] Cadeira Extensora - 4x 12 
        - [ ] Búlgaro - 3x 10-12
        - [ ] Elevação Pélvica - 3x 10 
        
        **Panturrilha**
        - [ ] Panturrilha - 4x 25-30
        """)

    with st.expander("TREINO C - Puxar (Costas, Trapézio, Bíceps, Antebraço)"):
        st.markdown("""
        **1. Costas**
        - [ ] Puxada Alta (Frente) - 4x 8-12
        - [ ] Remada Baixa (Barra) - 4x 8-12
        - [ ] Remada Serrote - 4x 8-12
        
        **2. Trapézio**
        - [ ] Encolhimento com Halteres - 3x 15
        
        **3. Bíceps**
        - [ ] Rosca Direta (Barra) - 4x 8-12
        - [ ] Rosca Inclinada - 3x 8-12
        - [ ] Rosca Martelo - 3x 8-12
        
        **4. Antebraço**
        - [ ] Rosca Inversa - 3x 8-12
        """)