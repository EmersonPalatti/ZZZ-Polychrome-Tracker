import streamlit as st
import pandas as pd
import plotly.express as px
import math
from datetime import datetime, date
import json

# Configuração inicial
st.set_page_config(layout="wide")
st.image('Site-logo-squaded.PNG', width=60)
st.title('ZZZ Polychrome Tracker')

# JavaScript para salvar no localStorage
st.markdown("""
<script>
function saveData(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}
document.saveTrackerData = saveData;
</script>
""", unsafe_allow_html=True)

# Função para definir os dados padrão
def get_default_data():
    return {
        'polychromes': 0,
        'encrypted_tapes': 0,
        'monochromes': 0,
        'master_tapes': 0,
        'limited_pity_count': 0,
        'wengine_count': 0,
        'standard_count': 0,
        'pb_polychrome': False,
        'pb_weapon': False,
        'residual_store': True,
        'is_pity': 'No'
    }

# Função para salvar dados no localStorage
def save_data(data):
    script = f"""
    <script>
    document.saveTrackerData('zzz_tracker_data', {json.dumps(data)});
    </script>
    """
    st.markdown(script, unsafe_allow_html=True)

# Inicializar session_state com dados padrão se não existir
if 'data' not in st.session_state:
    st.session_state.data = get_default_data()

# Funções auxiliares
def calculate_pulls(polychromes, monochromes, tapes, banner_count):
    return ((polychromes + monochromes) / 160) + tapes + banner_count

def generate_maintenance_dates(start_date='2025-04-22', periods=8, freq='42D'):
    maintance_dates = pd.date_range(start=start_date, periods=periods, freq=freq).date
    diff_dates = [(d - datetime.today().date()).days for d in maintance_dates]
    version = []
    current_version = 1.7
    for _ in range(periods):
        version.append(f'{current_version:.1f}')
        current_version += 0.1
        if current_version == 1.8:
            current_version = 2.0
    return pd.DataFrame({
        'Version Maintenance': version,
        'Maintenance Date': pd.to_datetime(maintance_dates),
        'Days To': diff_dates
    })

def calculate_expected_polychromes(days, pb_polychrome=False, pb_weapon=False):
    pb_polychrome_count = int(90 * days) if pb_polychrome else None
    pb_weapon_count = int(((160 * 4 / 42) + 780 / 42) * days) if pb_weapon else None
    return pd.DataFrame({
        "Activity/Event": [
            'Dailies', 'Ridu Weekly', 'Shiyu Defense', 'Deadly Assault', 'Hollow Zero',
            'Fading Signal Store', '7-D Login', 'Events (average)', 'Stream Codes',
            'Maintenance', 'Inter-Knot Membership', 'New Eridu City Fund'
        ],
        "Polychromes": [
            days * 60, int(days / 7 * 60), int(720 / 15 * days), int(days / 15 * 300),
            int(days / 7 * 160), int((160 * 5 / 30) * days), int((160 * 10 / 42) * days),
            int(2320 / 42 * days), int(300 / 42 * days), int(600 / 42 * days),
            pb_polychrome_count, pb_weapon_count
        ]
    })

# Função para atualizar os dados salvos
def update_data(key, value):
    st.session_state.data[key] = value
    save_data(st.session_state.data)

# Layout principal
col1, col2 = st.columns(2, border=True)

with col1:
    st.subheader(':material/account_balance_wallet: Current Currency', divider='gray')
    col3, col4 = st.columns(2)
    with col3:
        polychromes = st.number_input('**-> Current Polychromes**', value=st.session_state.data['polychromes'],
                                      placeholder='Input your polychromes', key='polychromes',
                                      on_change=lambda: update_data('polychromes', st.session_state.polychromes))
        encrypted_tapes = st.number_input('**-> Encrypted Master Tapes**', value=st.session_state.data['encrypted_tapes'],
                                          key='encrypted_tapes', on_change=lambda: update_data('encrypted_tapes', st.session_state.encrypted_tapes))
    with col4:
        monochromes = st.number_input('**-> Current Monochromes**', value=st.session_state.data['monochromes'],
                                      placeholder='Input your monochromes', key='monochromes',
                                      on_change=lambda: update_data('monochromes', st.session_state.monochromes))
        master_tapes = st.number_input('**-> Master Tapes**', value=st.session_state.data['master_tapes'],
                                       key='master_tapes', on_change=lambda: update_data('master_tapes', st.session_state.master_tapes))

    st.subheader('Current Pull Numbers', divider='gray')
    col5, col6, col7 = st.columns(3)
    with col5:
        limited_pity_count = st.number_input('**-> Limited Banner Pity Count**', value=st.session_state.data['limited_pity_count'],
                                             key='limited_pity_count', on_change=lambda: update_data('limited_pity_count', st.session_state.limited_pity_count))
    with col6:
        wengine_count = st.number_input('**-> W-Engine Banner**', value=st.session_state.data['wengine_count'],
                                        key='wengine_count', on_change=lambda: update_data('wengine_count', st.session_state.wengine_count))
    with col7:
        standard_count = st.number_input('**-> Standard Banner**', value=st.session_state.data['standard_count'],
                                         key='standard_count', on_change=lambda: update_data('standard_count', st.session_state.standard_count))

    st.subheader('Total of Pulls', divider='gray')
    col8, col9, col10 = st.columns(3)
    with col8:
        st.metric('**Total Limited Pulls Available**', int(calculate_pulls(polychromes, monochromes, encrypted_tapes, limited_pity_count)), border=True)
    with col9:
        st.metric('**W-Engine Banner Pulls**', int(calculate_pulls(polychromes, monochromes, encrypted_tapes, wengine_count)), border=True)
    with col10:
        st.metric('**Standard Banner Pulls**', int(calculate_pulls(polychromes, monochromes, master_tapes, standard_count)), border=True)

col30, col31 = st.columns(2, border=True)
m_dates = generate_maintenance_dates()

with col30:
    st.subheader(':material/calculate: Expected Polychrome Calculator', divider='gray')
    selection_values = pd.Series([0] + m_dates['Days To'].tolist())
    
    days_to_version = dict(zip(m_dates['Days To'], m_dates['Version Maintenance']))
    days_to_version[0] = 'Now'
    
    selected_days = st.segmented_control(
        ':material/edit_calendar: Select an option or enter custom days below',
        selection_values,
        format_func=lambda x: f'{x} days - v{days_to_version[x]}',
        default=selection_values[0]
    )
    days = st.number_input(
        'Days',
        min_value=0,
        value=selected_days if selected_days is not None else 0,
        step=1,
        label_visibility='collapsed'
    )
    
    col32, col33, col34 = st.columns(3)
    with col32:
        pb_polychrome = st.toggle('Inter-Knot Membership', value=st.session_state.data['pb_polychrome'],
                                  help='Polychrome Battle Pass', key='pb_polychrome',
                                  on_change=lambda: update_data('pb_polychrome', st.session_state.pb_polychrome))
    with col33:
        pb_weapon = st.toggle('New Eridu City Fund', value=st.session_state.data['pb_weapon'],
                              help='Weapon Battle Pass', key='pb_weapon',
                              on_change=lambda: update_data('pb_weapon', st.session_state.pb_weapon))
    
    df = calculate_expected_polychromes(days, pb_polychrome, pb_weapon)
    total_polychromes = df['Polychromes'].sum().astype(int)
    
    with col34:
        residual_store = st.toggle('Residual Signal Store', value=st.session_state.data['residual_store'],
                                   help='Converts pulls into Encrypted Master Tapes.', key='residual_store',
                                   on_change=lambda: update_data('residual_store', st.session_state.residual_store))
        limited_pulls = calculate_pulls(polychromes, monochromes, encrypted_tapes, limited_pity_count)
        residual_count = int(((((limited_pulls * 160 + total_polychromes) / 10) * 15) + (((limited_pulls * 160 + total_polychromes) / 76) * 40)) / 20) if residual_store else 0
    
    with col32:
        total_pulls = int(residual_count / 160 + (total_polychromes / 160))
        st.metric('Expected Total Pulls', total_pulls, border=True)
    
    with col33:
        total_polychromes_with_residual = int(total_polychromes + residual_count)
        st.metric('Expected Polychromes', total_polychromes_with_residual, border=True)
    
    with col34:
        total_attempts = total_pulls / 76
        st.metric('Expected Attempts', f'{total_attempts:.2f}', border=True, help='Total Pulls / 76')

    with st.expander('Polychrome Accumulation Graph'):
        cumulative_df = pd.DataFrame({
            'Day': range(days + 1),
            'Polychromes': [sum(
                [(d * 60), int(d / 7 * 60), int(720 / 15 * d), int(d / 15 * 300),
                 int(d / 7 * 160), int((160 * 5 / 30) * d), int((160 * 10 / 42) * d),
                 int(2320 / 42 * d), int(300 / 42 * d), int(600 / 42 * d),
                 int(90 * d) if pb_polychrome else 0,
                 int(((160 * 4 / 42) + 780 / 42) * d) if pb_weapon else 0]
            ) for d in range(days + 1)]
        })
        fig = px.line(cumulative_df, x='Day', y='Polychromes', title='Polychrome Accumulation Over Time',
                      labels={'Polychromes': 'Total Polychromes', 'Day': 'Days'},
                      template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

    with st.expander('Expected Maintenance Dates'):
        st.dataframe(m_dates, hide_index=True)

with col31:
    st.subheader(':material/table: Expected Polychrome Details', divider='gray')
    st.dataframe(df, hide_index=True)

with col2:
    st.subheader(':material/trending_up: Polychrome Calculator', divider='gray')
    universal_attempts = (limited_pulls + total_pulls) / 76
    st.metric('Total Polychrome Attempts', f'{universal_attempts:.2f}', border=True, help='Total Pulls / 76')
    
    is_pity = st.selectbox('Is on Guaranteed Pity?', ['No', 'Yes'], index=['No', 'Yes'].index(st.session_state.data['is_pity']),
                           key='is_pity', on_change=lambda: update_data('is_pity', st.session_state.is_pity))
    guaranteed_copies = math.floor(universal_attempts / 2 + (1 if is_pity == 'Yes' and universal_attempts % 2 != 0 else 0))
    st.metric('Guaranteed Copies', guaranteed_copies, border=True)
