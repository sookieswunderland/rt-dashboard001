# Hallo 

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

st.set_page_config(layout="wide")

st.title("Eine Analyse von Artikeln von RT")

# Datensatz laden
dataset_url = "https://github.com/polcomm-passau/computational_methods_python/raw/refs/heads/main/RT_D_Small.xlsx"
df = pd.read_excel(dataset_url)

# 'date' Spalte in Datumsformat umwandeln
df['date'] = pd.to_datetime(df['date'])

# Spalten für Reaktionen, Shares und Kommentare definieren
reaction_columns = ['haha', 'like', 'wow', 'angry', 'sad', 'love', 'hug']
engagement_columns = ['shares', 'comments_num']
all_metrics_columns = reaction_columns + engagement_columns

# --- Datumseingabe --- (Übung 3)
st.sidebar.header("Filteroptionen")
min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_range = st.sidebar.date_input(
    "Wähle einen Zeitraum aus:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered_by_date = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
else:
    df_filtered_by_date = df.copy()

# Eingabefeld für den Suchbegriff
search_term = st.sidebar.text_input("Bitte gib deinen Suchbegriff ein:", "")

# Filterbedingung für den Suchbegriff
search_condition = pd.Series([False] * len(df_filtered_by_date))
if search_term:
    search_condition = df_filtered_by_date['text'].fillna('').str.contains(search_term, case=False, na=False) | \
                       df_filtered_by_date['fulltext'].fillna('').str.contains(search_term, case=False, na=False)

# Filterung der DataFrames basierend auf Datum UND Suchbegriff
filtered_df_with_term = df_filtered_by_date[search_condition]
filtered_df_without_term = df_filtered_by_date[~search_condition]

# --- Liniendiagramm (Prozentualer Anteil) --- (Bestandteil des Originalprompts)
st.subheader("Entwicklung des Suchbegriffs im Zeitverlauf")
if search_term:
    total_posts_per_day = df_filtered_by_date['date'].dt.date.value_counts().sort_index()

    if not filtered_df_with_term.empty:
        filtered_posts_per_day = filtered_df_with_term['date'].dt.date.value_counts().sort_index()

        percentage_per_day = (filtered_posts_per_day / total_posts_per_day) * 100
        percentage_per_day = percentage_per_day.fillna(0) # Fülle NaN, falls an einem Tag keine Posts sind

        st.write(f"Prozentualer Anteil der Artikel mit '{search_term}' im Zeitraum vom {start_date} bis {end_date}")

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(percentage_per_day.index, percentage_per_day.values, marker='o', linestyle='-', color='skyblue')
        ax.set_title(f'Prozentualer Anteil der Posts pro Tag mit "{search_term}"')
        ax.set_xlabel('Datum')
        ax.set_ylabel('Prozentualer Anteil (%)')
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.warning(f"Keine Artikel gefunden, die '{search_term}' im Text oder Fulltext im ausgewählten Zeitraum enthalten.")
else:
    st.info("Bitte gib einen Suchbegriff ein, um die Analyse im Zeitverlauf zu sehen.")

# --- Vergleich der durchschnittlichen Metriken --- (Bestandteil des Originalprompts)
st.subheader("Vergleich der durchschnittlichen Metriken")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"### Artikel mit '{search_term}'")
    if not filtered_df_with_term.empty:
        st.metric(label="Gesamtzahl der Treffer", value=len(filtered_df_with_term))
        mean_metrics_with_term = filtered_df_with_term[all_metrics_columns].mean().round(2)
        st.dataframe(mean_metrics_with_term)
    else:
        st.info("Keine passenden Artikel gefunden.")

with col2:
    st.markdown(f"### Artikel ohne '{search_term}'")
    if not filtered_df_without_term.empty:
        st.metric(label="Gesamtzahl der Treffer", value=len(filtered_df_without_term))
        mean_metrics_without_term = filtered_df_without_term[all_metrics_columns].mean().round(2)
        st.dataframe(mean_metrics_without_term)
    else:
        st.info("Alle Artikel enthalten den Suchbegriff oder es wurde kein Suchbegriff eingegeben.")

with col3:
    st.markdown("### Unterschied (mit - ohne Suchbegriff)")
    if search_term and not filtered_df_with_term.empty and not filtered_df_without_term.empty:
        differences = mean_metrics_with_term - mean_metrics_without_term

        # Farben basierend auf dem Vorzeichen der Differenz zuweisen
        colors = ['red' if x > 0 else 'green' for x in differences.values]

        fig_diff, ax_diff = plt.subplots(figsize=(10, 6))
        sns.barplot(x=differences.values, y=differences.index, ax=ax_diff, palette=colors)
        ax_diff.set_title('Unterschiede der durchschnittlichen Metriken')
        ax_diff.set_xlabel('Differenz')
        ax_diff.set_ylabel('Metrik')
        ax_diff.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig_diff)
    else:
        st.info("Geben Sie einen Suchbegriff ein und stellen Sie sicher, dass sowohl Artikel mit als auch ohne den Begriff vorhanden sind, um die Unterschiede anzuzeigen.")

# --- Top Posts nach Reaktionstyp (Übung 2) ---
st.subheader("Top Posts nach Reaktionstyp")

if search_term:
    if not filtered_df_with_term.empty:
        selected_reaction = st.selectbox(
            "Wähle einen Reaktionstyp aus, um die Top 10 Posts anzuzeigen:",
            reaction_columns
        )

        if selected_reaction:
            st.markdown(f"### Top 10 Posts mit '{search_term}' und den meisten '{selected_reaction}' Reaktionen")
            top_posts = filtered_df_with_term.sort_values(by=selected_reaction, ascending=False).head(10)
            st.dataframe(top_posts[['text', selected_reaction]])
        else:
            st.info("Bitte wähle einen Reaktionstyp aus.")
    else:
        st.warning(f"Keine Artikel mit '{search_term}' im ausgewählten Zeitraum gefunden, um Top Posts anzuzeigen.")
else:
    st.info("Bitte gib einen Suchbegriff ein, um die Top Posts-Analyse zu aktivieren.")

st.subheader("Originale Daten (Auszug)")
st.dataframe(df.head())
