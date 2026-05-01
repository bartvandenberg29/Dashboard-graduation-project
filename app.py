import streamlit as st
import geopandas as gpd
import folium
import branca
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide", page_title="Suitability for Senior Housing Development")

@st.cache_data
def load_data():
    gdf = gpd.read_file("Candidate plots suitability layer.gpkg")
    return gdf.to_crs(epsg=4326)

@st.cache_data
def load_outline():
    # Vervang 'Gemeentegrens_Eindhoven.gpkg' door de echte bestandsnaam van je outline-laag
    outline_gdf = gpd.read_file("Eindhoven.gpkg")
    return outline_gdf.to_crs(epsg=4326)

outline = load_outline()

df = load_data()

st.title("Suitability for Senior Housing Development")

# --- SIDEBAR: GEWICHTEN ---
st.sidebar.header("Weights for Selection Criteria")
st.sidebar.write("Default values are results from an Analytic Hierarchy Process (AHP) survey conducted among experts in the field of senior housing.")

# 1. AHP basiswaarden (Hoofdcriteria)
ahp_main = {
    'amen': round(float(df['Weight_accessibility_daily_amenities'].iloc[0]), 3),
    'walk': round(float(df['Weight_neighborhood_walkability'].iloc[0]), 3),
    'env':  round(float(df['Weight_physical_environment'].iloc[0]), 3),
    'soc':  round(float(df['Weight_social_interaction_and_support'].iloc[0]), 3),
    'saf':  round(float(df['Weight_safety'].iloc[0]), 3)
}

# 1b. AHP sub-basiswaarden ophalen (zorg dat de kolomnamen exact kloppen met je gpkg)
ahp_sub = {
    'pt': round(float(df['Weight_public_transport'].iloc[0]), 3),
    'sm': round(float(df['weight_supermarket'].iloc[0]), 3),
    'gp': round(float(df['Weight_GP'].iloc[0]), 3),
    
    'cr': round(float(df['weight_safe_road_crossings'].iloc[0]), 3),
    'be': round(float(df['Weight_benches'].iloc[0]), 3),
    'li': round(float(df['Weight_street_lighting'].iloc[0]), 3),
    
    'gr': round(float(df['Weight_accessible_green'].iloc[0]), 3),
    'no': round(float(df['Weight_noise_level'].iloc[0]), 3),
    'ai': round(float(df['Weight_air_quality'].iloc[0]), 3),
    
    'in': round(float(df['Weight_social_interaction'].iloc[0]), 3),
    'co': round(float(df['Weight_social_cohesion'].iloc[0]), 3),
    'su': round(float(df['Weight_social_support'].iloc[0]), 3),
    
    'cm': round(float(df['Weight_crimes_committed'].iloc[0]), 3),
    'ns': round(float(df['Weight_perceived_neighborhood_safety'].iloc[0]), 3),
    'ts': round(float(df['Weight_perceived_traffic_safety'].iloc[0]), 3)
}

# 2. Initialiseer session_state met de AHP waarden
if 'w_amenities' not in st.session_state:
    st.session_state.w_amenities = ahp_main['amen']
    st.session_state.w_walkability = ahp_main['walk']
    st.session_state.w_environment = ahp_main['env']
    st.session_state.w_social = ahp_main['soc']
    st.session_state.w_safety = ahp_main['saf']
    
    # Koppel de sub-keys aan de ahp_sub waarden
    sub_map = {
        's_pt': 'pt', 's_sm': 'sm', 's_gp': 'gp',
        's_cr': 'cr', 's_be': 'be', 's_li': 'li',
        's_gr': 'gr', 's_no': 'no', 's_ai': 'ai',
        's_in': 'in', 's_co': 'co', 's_su': 'su',
        's_cm': 'cm', 's_ns': 'ns', 's_ts': 'ts'
    }
    for session_key, ahp_key in sub_map.items():
        st.session_state[session_key] = ahp_sub[ahp_key]

# 3. De Reset Functie (nu volledig op basis van AHP)
def reset_weights():
    st.session_state.w_amenities = ahp_main['amen']
    st.session_state.w_walkability = ahp_main['walk']
    st.session_state.w_environment = ahp_main['env']
    st.session_state.w_social = ahp_main['soc']
    st.session_state.w_safety = ahp_main['saf']
    
    sub_map = {
        's_pt': 'pt', 's_sm': 'sm', 's_gp': 'gp',
        's_cr': 'cr', 's_be': 'be', 's_li': 'li',
        's_gr': 'gr', 's_no': 'no', 's_ai': 'ai',
        's_in': 'in', 's_co': 'co', 's_su': 'su',
        's_cm': 'cm', 's_ns': 'ns', 's_ts': 'ts'
    }
    for session_key, ahp_key in sub_map.items():
        st.session_state[session_key] = ahp_sub[ahp_key]

st.sidebar.button("Reset to default AHP Weights", on_click=reset_weights)

# --- HOOFD SLIDERS ---
w_amenities = st.sidebar.slider("Accessibility of daily amenities", 0.0, 1.0, key="w_amenities", step=0.001)
with st.sidebar.expander("Weights for sub-criteria: Accessibility of daily amenities"):
    s_pt = st.slider("Public Transport", 0.0, 1.0, key="s_pt", step=0.01)
    s_sm = st.slider("Supermarket", 0.0, 1.0, key="s_sm", step=0.01)
    s_gp = st.slider("General practitioner", 0.0, 1.0, key="s_gp", step=0.01)
    st.text("Default AHP values: 0.39, 0.30, 0.32")

w_walkability = st.sidebar.slider("Neighborhood walkability", 0.0, 1.0, key="w_walkability", step=0.001)
with st.sidebar.expander("Weights for sub-criteria: Neighborhood walkability"):
    s_cr = st.slider("Safe road Crossings", 0.0, 1.0, key="s_cr", step=0.01)
    s_be = st.slider("Benches", 0.0, 1.0, key="s_be", step=0.01)
    s_li = st.slider("Street Lighting", 0.0, 1.0, key="s_li", step=0.01)
    st.text("Default AHP values: 0.30, 0.51, 0.18")

w_environment = st.sidebar.slider("Physical living environment", 0.0, 1.0, key="w_environment", step=0.001)
with st.sidebar.expander("Weights for sub-criteria: Physical living environment"):
    s_gr = st.slider("Quality and Quantity of Green", 0.0, 1.0, key="s_gr", step=0.01)
    s_no = st.slider("Noise Level", 0.0, 1.0, key="s_no", step=0.01)
    s_ai = st.slider("Air Quality", 0.0, 1.0, key="s_ai", step=0.01)
    st.text("Default AHP values: 0.48, 0.24, 0.28")

w_social = st.sidebar.slider("Social interaction and support", 0.0, 1.0, key="w_social", step=0.001)
with st.sidebar.expander("Weights for sub-criteria: Social interaction and support"):
    s_in = st.slider("Social interaction", 0.0, 1.0, key="s_in", step=0.01)
    s_co = st.slider("Social cohesion", 0.0, 1.0, key="s_co", step=0.01)
    s_su = st.slider("Social support", 0.0, 1.0, key="s_su", step=0.01)
    st.text("Default AHP values: 0.39, 0.30, 0.32")

w_safety = st.sidebar.slider("Safety", 0.0, 1.0, key="w_safety", step=0.001)
with st.sidebar.expander("Weights for sub-criteria: Safety"):
    s_cm = st.slider("Crime committed", 0.0, 1.0, key="s_cm", step=0.01)
    s_ns = st.slider("Perceived Safety", 0.0, 1.0, key="s_ns", step=0.01)
    s_ts = st.slider("Traffic Safety", 0.0, 1.0, key="s_ts", step=0.01)
    st.text("Default AHP values: 0.12, 0.55, 0.33")

st.sidebar.markdown("---")
st.sidebar.subheader("Default AHP Weights main criteria")

# Hoofdcriteria
st.sidebar.markdown(f"🛒 Accesibility of daily amenities: {ahp_main['amen']:.3f}")
st.sidebar.markdown(f"🚶 Neighborhood walkability: {ahp_main['walk']:.3f}")
st.sidebar.markdown(f"🌳 Physical living environment: {ahp_main['env']:.3f}")
st.sidebar.markdown(f"🤝 Social interaction and support: {ahp_main['soc']:.3f}")
st.sidebar.markdown(f"🛡️ Safety: {ahp_main['saf']:.3f}")
# --- DYNAMISCHE BEREKENING ---

# Bereken eerst de 5 tussen-scores op basis van de sub-sliders
def calc_sub(df, weights, scores):
    total = sum(weights)
    if total == 0: return 0
    return sum(df[s] * w for w, s in zip(weights, scores)) / total

df['dyn_score_amen'] = calc_sub(df, [s_pt, s_sm, s_gp], ['Suitability_score_public_transport', 'Suitability_score_supermarket', 'Suitability_score_GP'])
df['dyn_score_walk'] = calc_sub(df, [s_cr, s_be, s_li], ['Suitability_score_safe_crossings', 'Suitability_score_benches', 'Suitability_score_street_lighting'])
df['dyn_score_env']  = calc_sub(df, [s_gr, s_no, s_ai], ['Suitability_score_quality_and_quantity_green', 'Suitability_score_noise_level', 'Suitability_score_air_quality'])
df['dyn_score_soc']  = calc_sub(df, [s_in, s_co, s_su], ['Suitability_score_social_interaction', 'Suitability_score_social_cohesion', 'Suitability_score_social_support'])
df['dyn_score_saf']  = calc_sub(df, [s_cm, s_ns, s_ts], ['Suitability_score_crimes_committed', 'Suitability_score_perceived_neighborhood_safety', 'Suitability_score_perceived_traffic_safety'])

# Bereken de finale Suitability score
total_weight = w_amenities + w_walkability + w_environment + w_social + w_safety

if total_weight > 0:
    df['Suitability_score'] = (
        (df['dyn_score_amen'] * w_amenities +
         df['dyn_score_walk'] * w_walkability +
         df['dyn_score_env']  * w_environment +
         df['dyn_score_soc']  * w_social +
         df['dyn_score_saf']  * w_safety) 
        / total_weight
    )
else:
    df['Suitability_score'] = 0


# --- 3. KAART SECTIE ---
st.subheader("Map of the study area")

# 1. Voorbereiden van de data voor de kaart (df_display)
# We maken een kopie om de originele df niet te vervuilen
df_display = df.copy()

# Zorg dat de kolomnamen exact kloppen voor de tooltip en de kleuren
# We hernoemen de ID kolom voor een mooiere tooltip
if 'nationalCadastralReference' in df_display.columns:
    df_display = df_display.rename(columns={'nationalCadastralReference': 'Plot name'})

# Rond de score af voor de weergave
df_display['Suitability score'] = df_display['Suitability_score'].round(2)

# 2. Handgemaakte legenda
st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span style="font-size: 0.85rem; font-weight: bold;">0 (Low)</span>
        <div style="flex-grow: 1; max-width: 250px; height: 16px; background: linear-gradient(to right, #d7191c, #fdae61, #ffffbf, #a6d96a, #1a9641); border-radius: 4px; border: 1px solid #ccc;"></div>
        <span style="font-size: 0.85rem; font-weight: bold;">10 (High)</span>
    </div>
    """, unsafe_allow_html=True)

# 3. De kaart aanmaken
# Let op: 'column' moet exact matchen met de kolomnaam in df_display
m = df_display.explore(
    column='Suitability score', 
    cmap="RdYlGn", 
    tiles="CartoDB positron",
    vmin=0,
    vmax=12,
    style_kwds=dict(color="black", weight=1, fillOpacity=0.7),
    tooltip=['Plot name', 'Suitability score'], 
    popup=False,
    legend=False 
)

# Eindhoven outline toevoegen
outline.explore(m=m, color="red", style_kwds=dict(fillOpacity=0, weight=2, interactive=False), legend=False)

# De kaart tonen - width=None en use_container_width=True lost het zwarte blok op
st_data = st_folium(m, width=None, height=600, use_container_width=True)

st.markdown("---")

# --- 4. RAPPORT SECTIE (Onder de kaart) ---
if not st_data.get("last_active_drawing"):
    st.write("### 🔍 Location report")
    st.info("Select a plot on the map to see the detailed suitability report based on the criteria scores.")

else: 
    props = st_data["last_active_drawing"]["properties"]
    plot_id = props.get('Plot name')
    
    if plot_id:
        geselecteerd = df[df['nationalCadastralReference'] == plot_id].iloc[0]
        
        st.write(f"## 📋 Location report: {plot_id}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Suitability score", f"{round(geselecteerd['Suitability_score'], 1)} / 10")
        if 'Area' in df.columns:
            m2.metric("Area", f"{int(geselecteerd['Area'])} m²")
        
        st.write("### Scores per selection criterion")
        
        chart_data = {
            "Selection criteria": ["Accessibility of daily amenities", "Neighborhood walkability", "Physical living environment", "Social interaction and support", "Safety"],
            "Score": [
                geselecteerd['Suitability_score_accessibility_daily_amenities'],
                geselecteerd['Suitability_score_neighborhood_walkability'],
                geselecteerd['Suitability_score_physical_living_environment'],
                geselecteerd['Suitability_score_social_interaction_and_support'],
                geselecteerd['Suitability_score_safety']
            ]
        }
        
        fig = px.bar(
            chart_data, 
            x="Selection criteria", 
            y="Score", 
            range_y=[0, 10], 
            color="Score", 
            color_continuous_scale=[
                [0, "rgb(215, 25, 28)"],      # 0: Rood
                [0.4, "rgb(253, 174, 97)"],    # 4: Oranje
                [0.6, "rgb(255, 255, 191)"],   # 6: Geel (5 zit nu tussen oranje en geel in)
                [0.8, "rgb(166, 217, 106)"],   # 8: Lichtgroen
                [1, "rgb(26, 150, 65)"]        # 10: Donkergroen
            ],
            range_color=[0, 10],
            text_auto='.1f',
            height=400
        )
        
# Voeg deze regel toe om de hover-tekst te blokkeren
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

# Jouw bestaande layout blok
        fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="",
        yaxis_title="Score (0-10)"
        )
        
        # Ook de grafiek pakt nu de volle breedte onder de kaart
        st.plotly_chart(fig, use_container_width=True)

st.write("---")
st.write("### 🧩 Detailed Score Breakdown")
st.caption("Expand a criterion to adjust see a detailed report and adjust the weights of the sub-criteria to see how it affects the overall score")

# --- 4. RAPPORT SECTIE (Detail Breakdown met Sliders 0.0 - 1.0) ---
if 'geselecteerd' in locals() and geselecteerd is not None:
    # --- 1. AMENITIES ---
    # --- VOORBEELD VOOR DE AMENITIES SECTIE ---
    with st.expander("🛒 Accessibility of daily amenities - Detailed Breakdown"):

    # 2. Middenstuk: Links de grafiek, Rechts de berekening van de gewichten
        col_graph, col_spacer, col_weights = st.columns([2, 0.1, 1.9])

    with col_graph:
        if 'geselecteerd' in locals() and geselecteerd is not None:
            current_score = float(geselecteerd['dyn_score_amen'])
            st.metric("Criterion Score", f"{current_score:.1f} / 10")
            
            sub_scores = [
                geselecteerd['Suitability_score_public_transport'], 
                geselecteerd['Suitability_score_supermarket'], 
                geselecteerd['Suitability_score_GP']
            ]
            
            fig_sub = px.bar(
            x=["Public transport", "Supermarket", "General practitioner"], 
            y=sub_scores, 
            range_y=[0, 10], 
            color=sub_scores,
            color_continuous_scale=[
                [0, "rgb(215, 25, 28)"], 
                [0.4, "rgb(253, 174, 97)"], 
                [0.6, "rgb(255, 255, 191)"], 
                [0.8, "rgb(166, 217, 106)"], 
                [1, "rgb(26, 150, 65)"]
            ],
        range_color=[0, 10], 
        text_auto='.1f', 
        height=400
    )

# 1. Schakel hover volledig uit voor deze specifieke grafiek
        fig_sub.update_traces(hoverinfo='none', hovertemplate=None)

# 2. Pas de titel van de kleurenbalk aan en behoud de overige layout instellingen
        fig_sub.update_layout(
        margin=dict(l=10, r=10, t=5, b=5), 
        xaxis_title="", 
        yaxis_title="Score (0-10)", 
        showlegend=False,
        coloraxis_colorbar=dict(title="Score") # Verandert 'color' naar 'Score'
    )

        st.plotly_chart(fig_sub, use_container_width=True)

    with col_weights:
        st.markdown("### ⚖️ Chosen sub criterion weights")
        # Dit bootst de rechterkant van je plaatje na
        st.write(f"Weight Public Transport: **{s_pt:.2f}**")
        st.write(f"Weight Supermarket: **{s_sm:.2f}**")
        st.write(f"Weight General practitioner: **{s_gp:.2f}**")
        
        st.markdown("---")
        total_amen_weights = s_pt + s_sm + s_gp
        st.write(f"**Sum of weights:** `{s_pt:.2f} + {s_sm:.2f} + {s_gp:.2f} = {total_amen_weights:.2f}`")

    # 3. Regel over de hele breedte met de scores per sub-criterium
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Public transport", f"{sub_scores[0]:.1f}")
        m2.metric("Supermarket", f"{sub_scores[1]:.1f}")
        m3.metric("General practitioner", f"{sub_scores[2]:.1f}")

    # 4. Afsluitende regel met de volledige berekening
        st.info(f"**Suitability Score** = (({sub_scores[0]:.1f} × {s_pt:.2f}) + ({sub_scores[1]:.1f} × {s_sm:.2f}) + ({sub_scores[2]:.1f} × {s_gp:.2f})) / {total_amen_weights:.2f} = **{current_score:.1f}**")
     
    # --- 2. WALKABILITY ---
    with st.expander("🚶 Neighborhood walkability - Detailed Breakdown"):
        col_graph, col_spacer, col_weights = st.columns([2, 0.1, 1.9])

    with col_graph:
        if 'geselecteerd' in locals() and geselecteerd is not None:
            current_score = float(geselecteerd['dyn_score_walk'])
            st.metric("Criterion Score", f"{current_score:.1f} / 10")
            
            sub_scores = [
                geselecteerd['Suitability_score_safe_crossings'], 
                geselecteerd['Suitability_score_benches'], 
                geselecteerd['Suitability_score_street_lighting']
            ]
            
            fig_walk = px.bar(
                x=["Safe Road Crossings", "Benches", "Street Lighting"], 
                y=sub_scores, range_y=[0, 10], color=sub_scores,
                color_continuous_scale=[[0, "rgb(215, 25, 28)"], [0.4, "rgb(253, 174, 97)"], [0.6, "rgb(255, 255, 191)"], [0.8, "rgb(166, 217, 106)"], [1, "rgb(26, 150, 65)"]],
                range_color=[0, 10], text_auto='.1f', height=400
            )
            fig_walk.update_traces(hoverinfo='none', hovertemplate=None)
            fig_walk.update_layout(margin=dict(l=10, r=10, t=5, b=5), xaxis_title="", yaxis_title="Score (0-10)", showlegend=False, coloraxis_colorbar=dict(title="Score"))
            st.plotly_chart(fig_walk, use_container_width=True)

    with col_weights:
        st.markdown("### ⚖️ Chosen sub criterion weights")
        st.write(f"Weight Safe Road Crossings: **{s_cr:.2f}**")
        st.write(f"Weight Benches: **{s_be:.2f}**")
        st.write(f"Weight Street Lighting: **{s_li:.2f}**")
        st.markdown("---")
        total_weights = s_cr + s_be + s_li
        st.write(f"**Sum of weights:** `{s_cr:.2f} + {s_be:.2f} + {s_li:.2f} = {total_weights:.2f}`")

        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Safe Road Crossings", f"{sub_scores[0]:.1f}")
        m2.metric("Benches", f"{sub_scores[1]:.1f}")
        m3.metric("Street Lighting", f"{sub_scores[2]:.1f}")

        st.info(f"**Suitability Score** = (({sub_scores[0]:.1f} × {s_cr:.2f}) + ({sub_scores[1]:.1f} × {s_be:.2f}) + ({sub_scores[2]:.1f} × {s_li:.2f})) / {total_weights:.2f} = **{current_score:.1f}**")

    # --- 3. ENVIRONMENT ---
    with st.expander("🌳 Physical living environment - Detailed Breakdown"):
        col_graph, col_spacer, col_weights = st.columns([2, 0.1, 1.9])

    with col_graph:
        if 'geselecteerd' in locals() and geselecteerd is not None:
            current_score = float(geselecteerd['dyn_score_env'])
            st.metric("Criterion Score", f"{current_score:.1f} / 10")
            
            sub_scores = [
                geselecteerd['Suitability_score_quality_and_quantity_green'], 
                geselecteerd['Suitability_score_noise_level'], 
                geselecteerd['Suitability_score_air_quality']
            ]
            
            fig_env = px.bar(
                x=["Quality and quantity of green", "Noise Level", "Air Quality"], 
                y=sub_scores, range_y=[0, 10], color=sub_scores,
                color_continuous_scale=[[0, "rgb(215, 25, 28)"], [0.4, "rgb(253, 174, 97)"], [0.6, "rgb(255, 255, 191)"], [0.8, "rgb(166, 217, 106)"], [1, "rgb(26, 150, 65)"]],
                range_color=[0, 10], text_auto='.1f', height=400
            )
            fig_env.update_traces(hoverinfo='none', hovertemplate=None)
            fig_env.update_layout(margin=dict(l=10, r=10, t=5, b=5), xaxis_title="", yaxis_title="Score (0-10)", showlegend=False, coloraxis_colorbar=dict(title="Score"))
            st.plotly_chart(fig_env, use_container_width=True)

    with col_weights:
        st.markdown("### ⚖️ Chosen sub criterion weights")
        st.write(f"Weight Quality and quantity of green: **{s_gr:.2f}**")
        st.write(f"Weight Noise Level: **{s_no:.2f}**")
        st.write(f"Weight Air Quality: **{s_ai:.2f}**")
        st.markdown("---")
        total_weights = s_gr + s_no + s_ai
        st.write(f"**Sum of weights:** `{s_gr:.2f} + {s_no:.2f} + {s_ai:.2f} = {total_weights:.2f}`")

        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Quality and quantity of green", f"{sub_scores[0]:.1f}")
        m2.metric("Noise Level", f"{sub_scores[1]:.1f}")
        m3.metric("Air Quality", f"{sub_scores[2]:.1f}")

        st.info(f"**Suitability Score** = (({sub_scores[0]:.1f} × {s_gr:.2f}) + ({sub_scores[1]:.1f} × {s_no:.2f}) + ({sub_scores[2]:.1f} × {s_ai:.2f})) / {total_weights:.2f} = **{current_score:.1f}**")

    # --- 4. SOCIAL ---
    with st.expander("🤝 Social interaction and support - Detailed Breakdown"):
        col_graph, col_spacer, col_weights = st.columns([2, 0.1, 1.9])

    with col_graph:
        if 'geselecteerd' in locals() and geselecteerd is not None:
            current_score = float(geselecteerd['dyn_score_soc'])
            st.metric("Criterion Score", f"{current_score:.1f} / 10")
            
            sub_scores = [
                geselecteerd['Suitability_score_social_interaction'], 
                geselecteerd['Suitability_score_social_cohesion'], 
                geselecteerd['Suitability_score_social_support']
            ]
            
            fig_soc = px.bar(
                x=["Social Interaction", "Social Cohesion", "Social Support"], 
                y=sub_scores, range_y=[0, 10], color=sub_scores,
                color_continuous_scale=[[0, "rgb(215, 25, 28)"], [0.4, "rgb(253, 174, 97)"], [0.6, "rgb(255, 255, 191)"], [0.8, "rgb(166, 217, 106)"], [1, "rgb(26, 150, 65)"]],
                range_color=[0, 10], text_auto='.1f', height=400
            )
            fig_soc.update_traces(hoverinfo='none', hovertemplate=None)
            fig_soc.update_layout(margin=dict(l=10, r=10, t=5, b=5), xaxis_title="", yaxis_title="Score (0-10)", showlegend=False, coloraxis_colorbar=dict(title="Score"))
            st.plotly_chart(fig_soc, use_container_width=True)

    with col_weights:
        st.markdown("### ⚖️ Chosen sub criterion weights")
        st.write(f"Weight Social Interaction: **{s_in:.2f}**")
        st.write(f"Weight Social Cohesion: **{s_co:.2f}**")
        st.write(f"Weight Social Support: **{s_su:.2f}**")
        st.markdown("---")
        total_weights = s_in + s_co + s_su
        st.write(f"**Sum of weights:** `{s_in:.2f} + {s_co:.2f} + {s_su:.2f} = {total_weights:.2f}`")

        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Social Interaction", f"{sub_scores[0]:.1f}")
        m2.metric("Social Cohesion", f"{sub_scores[1]:.1f}")
        m3.metric("Social Support", f"{sub_scores[2]:.1f}")

        st.info(f"**Suitability Score** = (({sub_scores[0]:.1f} × {s_in:.2f}) + ({sub_scores[1]:.1f} × {s_co:.2f}) + ({sub_scores[2]:.1f} × {s_su:.2f})) / {total_weights:.2f} = **{current_score:.1f}**")

    # --- 5. SAFETY ---
    with st.expander("🛡️ Safety - Detailed Breakdown"):
        col_graph, col_spacer, col_weights = st.columns([2, 0.1, 1.9])

    with col_graph:
        if 'geselecteerd' in locals() and geselecteerd is not None:
            current_score = float(geselecteerd['dyn_score_saf'])
            st.metric("Criterion Score", f"{current_score:.1f} / 10")
            
            sub_scores = [
                geselecteerd['Suitability_score_crimes_committed'], 
                geselecteerd['Suitability_score_perceived_neighborhood_safety'], 
                geselecteerd['Suitability_score_perceived_traffic_safety']
            ]
            
            fig_saf = px.bar(
                x=["Crimes Committed", "Neighborhood Safety", "Traffic Safety"], 
                y=sub_scores, range_y=[0, 10], color=sub_scores,
                color_continuous_scale=[[0, "rgb(215, 25, 28)"], [0.4, "rgb(253, 174, 97)"], [0.6, "rgb(255, 255, 191)"], [0.8, "rgb(166, 217, 106)"], [1, "rgb(26, 150, 65)"]],
                range_color=[0, 10], text_auto='.1f', height=400
            )
            fig_saf.update_traces(hoverinfo='none', hovertemplate=None)
            fig_saf.update_layout(margin=dict(l=10, r=10, t=5, b=5), xaxis_title="", yaxis_title="Score (0-10)", showlegend=False, coloraxis_colorbar=dict(title="Score"))
            st.plotly_chart(fig_saf, use_container_width=True)

    with col_weights:
        st.markdown("### ⚖️ Chosen sub criterion weights")
        st.write(f"Weight Crimes Committed: **{s_cm:.2f}**")
        st.write(f"Weight Neighborhood Safety: **{s_ns:.2f}**")
        st.write(f"Weight Traffic Safety: **{s_ts:.2f}**")
        st.markdown("---")
        total_weights = s_cm + s_ns + s_ts
        st.write(f"**Sum of weights:** `{s_cm:.2f} + {s_ns:.2f} + {s_ts:.2f} = {total_weights:.2f}`")

        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Crimes Committed", f"{sub_scores[0]:.1f}")
        m2.metric("Neighborhood Safety", f"{sub_scores[1]:.1f}")
        m3.metric("Traffic Safety", f"{sub_scores[2]:.1f}")

        st.info(f"**Suitability Score** = (({sub_scores[0]:.1f} × {s_cm:.2f}) + ({sub_scores[1]:.1f} × {s_ns:.2f}) + ({sub_scores[2]:.1f} × {s_ts:.2f})) / {total_weights:.2f} = **{current_score:.1f}**")