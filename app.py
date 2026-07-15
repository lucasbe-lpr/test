import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# ------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ------------------------------------------------------------
st.set_page_config(page_title="Météo Express - Journalist Tool", layout="wide")
st.title("🌦️ Météo Express – outil pour journalistes")
st.markdown("---")

# ------------------------------------------------------------
# 2. CHARGEMENT DES DONNÉES (avec cache)
# ------------------------------------------------------------
@st.cache_data
def load_data(uploaded_file=None):
    """
    Charge le CSV depuis un upload ou depuis un fichier par défaut.
    Retourne : df (DataFrame), metadatas (dict)
    """
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep=';', low_memory=False)
    else:
        # Fichier par défaut : on suppose qu'il est dans le même répertoire
        # ou bien on laisse l'utilisateur le charger obligatoirement.
        # Pour l'exemple, on propose un placeholder.
        st.warning("Veuillez charger un fichier CSV en utilisant le bouton ci-dessous.")
        return None, None

    # Nettoyage
    df.columns = df.columns.str.strip()
    # Convertir la date
    if 'AAAAMMJJ' in df.columns:
        df['AAAAMMJJ'] = pd.to_datetime(df['AAAAMMJJ'], format='%d/%m/%Y', errors='coerce')
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        st.error("Colonne de date non trouvée (AAAAMMJJ ou date).")
        return None, None

    # Remplacer les valeurs vides ou ';' par NaN
    df = df.replace(';', pd.NA).replace('', pd.NA)
    # Convertir les colonnes numériques (sauf codes qualité et métadonnées)
    for col in df.columns:
        if col.startswith('Q') or col in ['NUM_POSTE', 'NOM_USUEL', 'LAT', 'LON', 'ALTI', '__id']:
            continue
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Extraire les métadonnées (on prend la première ligne)
    meta = {}
    if 'NUM_POSTE' in df.columns:
        meta['NUM_POSTE'] = df['NUM_POSTE'].iloc[0]
    if 'NOM_USUEL' in df.columns:
        meta['NOM_USUEL'] = df['NOM_USUEL'].iloc[0]
    if 'LAT' in df.columns:
        meta['LAT'] = df['LAT'].iloc[0]
    if 'LON' in df.columns:
        meta['LON'] = df['LON'].iloc[0]
    if 'ALTI' in df.columns:
        meta['ALTI'] = df['ALTI'].iloc[0]

    return df, meta

# ------------------------------------------------------------
# 3. INTERFACE DE CHARGEMENT
# ------------------------------------------------------------
uploaded_file = st.sidebar.file_uploader("Charger un fichier CSV", type="csv")

if uploaded_file is None:
    st.info("🔍 Chargez un fichier CSV pour commencer.")
    st.stop()

df, meta = load_data(uploaded_file)
if df is None:
    st.stop()

# Afficher les métadonnées dans la barre latérale
st.sidebar.subheader("📌 Station")
if meta:
    st.sidebar.write(f"**Nom** : {meta.get('NOM_USUEL', 'Inconnu')}")
    st.sidebar.write(f"**N° poste** : {meta.get('NUM_POSTE', '')}")
    st.sidebar.write(f"**Altitude** : {meta.get('ALTI', '')} m")
    st.sidebar.write(f"**Lat/Lon** : {meta.get('LAT', '')} / {meta.get('LON', '')}")
st.sidebar.markdown("---")

# ------------------------------------------------------------
# 4. FILTRES (barre latérale)
# ------------------------------------------------------------
# Déterminer les colonnes de paramètres (exclure métadonnées et codes qualité)
exclude_cols = ['__id', 'NUM_POSTE', 'NOM_USUEL', 'LAT', 'LON', 'ALTI', 'AAAAMMJJ']
# Les colonnes commençant par Q sont des codes qualité
param_cols = [c for c in df.columns if c not in exclude_cols and not c.startswith('Q')]
# On peut aussi ajouter les colonnes de codes qualité pour le filtrage
qual_cols = [c for c in df.columns if c.startswith('Q')]

# Filtre date
date_min = df['AAAAMMJJ'].min()
date_max = df['AAAAMMJJ'].max()
if pd.isna(date_min) or pd.isna(date_max):
    st.error("Erreur de dates.")
    st.stop()

start_date = st.sidebar.date_input("Date de début", date_min, min_value=date_min, max_value=date_max)
end_date = st.sidebar.date_input("Date de fin", date_max, min_value=date_min, max_value=date_max)

# Filtre paramètres (multi-sélection)
selected_params = st.sidebar.multiselect(
    "Paramètres à afficher",
    options=param_cols,
    default=param_cols[:3] if len(param_cols) >= 3 else param_cols
)

# Filtre qualité : exclure les données avec code qualité = 2 (douteux) ?
exclude_doubtful = st.sidebar.checkbox("Exclure les données douteuses (code qualité = 2)", value=False)
# Option : exclure aussi les données non validées (9) ?
exclude_filtered = st.sidebar.checkbox("Exclure les données filtrées (code qualité = 9)", value=False)

# Appliquer les filtres sur le DataFrame
mask = (df['AAAAMMJJ'] >= pd.to_datetime(start_date)) & (df['AAAAMMJJ'] <= pd.to_datetime(end_date))

# Filtre qualité : pour chaque colonne de paramètre sélectionnée, on vérifie son code qualité associé (Q+nom)
for param in selected_params:
    qcol = f"Q{param}"
    if qcol in df.columns:
        if exclude_doubtful:
            mask &= (df[qcol] != 2)
        if exclude_filtered:
            mask &= (df[qcol] != 9)
    # Si pas de code qualité, on ignore

df_filtered = df.loc[mask].copy()

if df_filtered.empty:
    st.warning("Aucune donnée après filtrage.")
    st.stop()

# ------------------------------------------------------------
# 5. ONGLETS
# ------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Aperçu", "📈 Graphiques", "🏆 Records", "⚖️ Comparaison", "📤 Export"])

# ------------------------------------------------------------
# ONGLET 1 : APERÇU
# ------------------------------------------------------------
with tab1:
    st.subheader("Aperçu des données filtrées")
    st.write(f"Période : {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')} – {len(df_filtered)} jours")

    # Statistiques rapides
    st.markdown("**Statistiques sommaires**")
    cols_stats = [c for c in selected_params if c in df_filtered.columns and df_filtered[c].notna().any()]
    if cols_stats:
        stats = df_filtered[cols_stats].describe(percentiles=[.25, .5, .75]).round(2)
        st.dataframe(stats, use_container_width=True)
    else:
        st.info("Aucune donnée numérique pour les paramètres sélectionnés.")

    st.markdown("**Données détaillées**")
    # On affiche les colonnes utiles : date + paramètres + leurs codes qualité éventuels
    show_cols = ['AAAAMMJJ'] + selected_params
    # Ajouter les codes qualité correspondants
    for p in selected_params:
        qc = f"Q{p}"
        if qc in df_filtered.columns:
            show_cols.append(qc)
    # Filtrer les colonnes existantes
    show_cols = [c for c in show_cols if c in df_filtered.columns]
    st.dataframe(df_filtered[show_cols].sort_values('AAAAMMJJ'), use_container_width=True)

# ------------------------------------------------------------
# ONGLET 2 : GRAPHIQUES
# ------------------------------------------------------------
with tab2:
    st.subheader("Visualisation des séries temporelles")

    if not selected_params:
        st.info("Sélectionnez au moins un paramètre dans la barre latérale.")
    else:
        # Choix du type de graphique
        chart_type = st.radio("Type de graphique", ["Ligne", "Barres", "Nuage de points"], horizontal=True)
        # Option moyenne mobile
        show_ma = st.checkbox("Ajouter une moyenne mobile (7 jours)")

        # Créer le graphique
        fig = go.Figure()
        for param in selected_params:
            if param not in df_filtered.columns:
                continue
            y = df_filtered[param]
            x = df_filtered['AAAAMMJJ']
            # Masquer les NaN
            mask_valid = y.notna()
            x_valid = x[mask_valid]
            y_valid = y[mask_valid]

            if chart_type == "Ligne":
                fig.add_trace(go.Scatter(x=x_valid, y=y_valid, mode='lines+markers', name=param))
            elif chart_type == "Barres":
                fig.add_trace(go.Bar(x=x_valid, y=y_valid, name=param))
            else:  # Nuage
                fig.add_trace(go.Scatter(x=x_valid, y=y_valid, mode='markers', name=param))

            # Moyenne mobile
            if show_ma and len(y_valid) > 7:
                ma = y_valid.rolling(7, min_periods=1).mean()
                fig.add_trace(go.Scatter(x=x_valid, y=ma, mode='lines',
                                         name=f"{param} (moy. mobile 7j)",
                                         line=dict(dash='dash')))

        fig.update_layout(
            title=f"Évolution des paramètres du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}",
            xaxis_title="Date",
            yaxis_title="Valeur",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
# ONGLET 3 : RECORDS
# ------------------------------------------------------------
with tab3:
    st.subheader("Records et extrêmes")

    # Sélection du paramètre pour les records
    record_param = st.selectbox("Paramètre pour les records", options=selected_params if selected_params else param_cols)
    if record_param and record_param in df_filtered.columns:
        col_data = df_filtered[record_param]
        # Top 10 maximum
        top_max = df_filtered.nlargest(10, record_param)[['AAAAMMJJ', record_param]].dropna()
        # Top 10 minimum
        top_min = df_filtered.nsmallest(10, record_param)[['AAAAMMJJ', record_param]].dropna()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🔥 Top 10 des valeurs maximales de {record_param}**")
            if not top_max.empty:
                top_max['AAAAMMJJ'] = top_max['AAAAMMJJ'].dt.strftime('%d/%m/%Y')
                st.dataframe(top_max, use_container_width=True)
            else:
                st.info("Pas de données.")
        with col2:
            st.markdown(f"**❄️ Top 10 des valeurs minimales de {record_param}**")
            if not top_min.empty:
                top_min['AAAAMMJJ'] = top_min['AAAAMMJJ'].dt.strftime('%d/%m/%Y')
                st.dataframe(top_min, use_container_width=True)
            else:
                st.info("Pas de données.")

        # Graphique des extrêmes
        st.markdown("**Visualisation des extrêmes sur la période**")
        # On récupère les dates des records
        record_dates = pd.concat([top_max, top_min])['AAAAMMJJ'].unique()
        # On affiche la série complète avec mise en évidence des points records
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_filtered['AAAAMMJJ'], y=df_filtered[record_param],
            mode='lines', name='Série', line=dict(color='lightgray')
        ))
        # Points max
        fig2.add_trace(go.Scatter(
            x=top_max['AAAAMMJJ'], y=top_max[record_param],
            mode='markers', name='Max', marker=dict(color='red', size=10)
        ))
        # Points min
        fig2.add_trace(go.Scatter(
            x=top_min['AAAAMMJJ'], y=top_min[record_param],
            mode='markers', name='Min', marker=dict(color='blue', size=10)
        ))
        fig2.update_layout(
            title=f"Records de {record_param}",
            xaxis_title="Date",
            yaxis_title=record_param
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Résumé texte automatique
        if not top_max.empty:
            max_val = top_max.iloc[0][record_param]
            max_date = top_max.iloc[0]['AAAAMMJJ'].strftime('%d/%m/%Y')
            st.success(f"✅ Le **{max_date}**, la valeur de **{record_param}** a atteint **{max_val}**, soit le maximum sur la période sélectionnée.")

        if not top_min.empty:
            min_val = top_min.iloc[0][record_param]
            min_date = top_min.iloc[0]['AAAAMMJJ'].strftime('%d/%m/%Y')
            st.info(f"❄️ Le **{min_date}**, la valeur de **{record_param}** est descendue à **{min_val}**, soit le minimum sur la période sélectionnée.")
    else:
        st.info("Sélectionnez un paramètre valide.")

# ------------------------------------------------------------
# ONGLET 4 : COMPARAISON
# ------------------------------------------------------------
with tab4:
    st.subheader("Comparer deux périodes")

    # Sélection des paramètres à comparer
    compare_params = st.multiselect(
        "Paramètres à comparer",
        options=selected_params if selected_params else param_cols,
        default=selected_params[:2] if len(selected_params) >= 2 else selected_params
    )

    if not compare_params:
        st.info("Sélectionnez au moins un paramètre.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Période A**")
            start_a = st.date_input("Début A", date_min, key="start_a", min_value=date_min, max_value=date_max)
            end_a = st.date_input("Fin A", date_max, key="end_a", min_value=date_min, max_value=date_max)
        with col_b:
            st.markdown("**Période B**")
            start_b = st.date_input("Début B", date_min, key="start_b", min_value=date_min, max_value=date_max)
            end_b = st.date_input("Fin B", date_max, key="end_b", min_value=date_min, max_value=date_max)

        # Filtrer les deux périodes
        mask_a = (df['AAAAMMJJ'] >= pd.to_datetime(start_a)) & (df['AAAAMMJJ'] <= pd.to_datetime(end_a))
        mask_b = (df['AAAAMMJJ'] >= pd.to_datetime(start_b)) & (df['AAAAMMJJ'] <= pd.to_datetime(end_b))
        df_a = df.loc[mask_a].copy()
        df_b = df.loc[mask_b].copy()

        if df_a.empty or df_b.empty:
            st.warning("L'une des périodes ne contient pas de données.")
        else:
            # Statistiques comparatives
            st.markdown("**Comparaison statistique**")
            stats_a = df_a[compare_params].describe(percentiles=[.25, .5, .75]).round(2)
            stats_b = df_b[compare_params].describe(percentiles=[.25, .5, .75]).round(2)
            # Renommer les colonnes pour distinguer
            stats_a.columns = [f"{c} (A)" for c in stats_a.columns]
            stats_b.columns = [f"{c} (B)" for c in stats_b.columns]
            concat_stats = pd.concat([stats_a, stats_b], axis=1)
            st.dataframe(concat_stats, use_container_width=True)

            # Graphique superposé
            st.markdown("**Évolution comparée**")
            fig_comp = go.Figure()
            for param in compare_params:
                if param not in df_a.columns or param not in df_b.columns:
                    continue
                # Période A
                fig_comp.add_trace(go.Scatter(
                    x=df_a['AAAAMMJJ'], y=df_a[param],
                    mode='lines', name=f"{param} (A)", line=dict(dash='solid')
                ))
                # Période B
                fig_comp.add_trace(go.Scatter(
                    x=df_b['AAAAMMJJ'], y=df_b[param],
                    mode='lines', name=f"{param} (B)", line=dict(dash='dot')
                ))
            fig_comp.update_layout(
                title="Comparaison des périodes",
                xaxis_title="Date",
                yaxis_title="Valeur",
                hovermode="x unified"
            )
            st.plotly_chart(fig_comp, use_container_width=True)

# ------------------------------------------------------------
# ONGLET 5 : EXPORT
# ------------------------------------------------------------
with tab5:
    st.subheader("Exporter les données et graphiques")

    # Export CSV des données filtrées
    csv_data = df_filtered.to_csv(sep=';', index=False, decimal=',')
    st.download_button(
        label="📥 Télécharger les données filtrées (CSV)",
        data=csv_data,
        file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    # Export des graphiques ? Streamlit + Plotly permet le téléchargement direct via le menu du graphique.
    st.info("💡 Les graphiques peuvent être téléchargés en PNG/SVG via le menu de chaque graphique (icône appareil photo).")

st.sidebar.markdown("---")
st.sidebar.caption("Développé avec ❤️ pour les journalistes – données Météo-France")
