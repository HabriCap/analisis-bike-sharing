from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid")

REQUIRED_COLUMNS = {
    "dteday",
    "season_label",
    "year",
    "workingday",
    "hr",
    "cnt",
    "casual",
    "registered",
    "temp_c",
    "hum_pct",
    "windspeed_kmh",
}
TIME_CLUSTER_ORDER = [
    "1. Dini Hari (00-05)",
    "2. Jam Sibuk Pagi (06-09)",
    "3. Siang Hari (10-15)",
    "4. Jam Sibuk Sore (16-19)",
    "5. Malam Hari (20-23)",
]
SEASON_ORDER = ["Spring", "Summer", "Fall", "Winter"]
WEEKDAY_ORDER = [
    "Minggu",
    "Senin",
    "Selasa",
    "Rabu",
    "Kamis",
    "Jumat",
    "Sabtu",
]
WEATHER_LABELS = {
    "temp_c": "Suhu (°C)",
    "hum_pct": "Kelembapan (%)",
    "windspeed_kmh": "Kecepatan angin (km/jam)",
}


@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "main_data.csv"
    df = pd.read_csv(data_path)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError(
            "Kolom wajib tidak ditemukan di main_data.csv: "
            + ", ".join(sorted(missing_columns))
        )
    df["dteday"] = pd.to_datetime(df["dteday"], errors="raise")
    return df


df = load_data()

st.title("Bike Sharing Analytics Dashboard")
st.markdown(
    "Analisis penyewaan sepeda berdasarkan waktu, musim, cuaca, dan profil pengguna "
    "selama 2011–2012."
)

st.sidebar.header("Filter Data")
min_date = df["dteday"].min().date()
max_date = df["dteday"].max().date()
date_range = st.sidebar.date_input(
    "Rentang waktu",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(date_range) != 2:
    st.info("Pilih tanggal mulai dan tanggal akhir untuk menampilkan analisis.")
    st.stop()

start_date, end_date = date_range
seasons = sorted(df["season_label"].dropna().unique().tolist())
selected_seasons = st.sidebar.multiselect(
    "Musim",
    options=seasons,
    default=seasons,
)

main_df = df.loc[
    df["dteday"].dt.date.between(start_date, end_date)
    & df["season_label"].isin(selected_seasons)
].copy()

if main_df.empty:
    st.info("Tidak ada data untuk rentang tanggal dan musim yang dipilih.")
    st.stop()

metric_columns = st.columns(4)
metric_columns[0].metric(
    "Total penyewaan",
    f"{main_df['cnt'].sum():,}",
)
metric_columns[1].metric(
    "Rata-rata penyewaan per jam",
    f"{main_df['cnt'].mean():,.1f}",
)
metric_columns[2].metric(
    "Pengguna terdaftar",
    f"{main_df['registered'].sum():,}",
)
metric_columns[3].metric(
    "Pengguna kasual",
    f"{main_df['casual'].sum():,}",
)

st.divider()
st.subheader("Ringkasan penyewaan per musim")
daily_totals = (
    main_df.groupby(["dteday", "year", "season_label"], as_index=False)["cnt"]
    .sum()
)
season_summary = (
    daily_totals.groupby(["season_label", "year"], as_index=False)["cnt"]
    .mean()
)
fig0, ax0 = plt.subplots(figsize=(10, 4))
sns.barplot(
    data=season_summary,
    x="season_label",
    y="cnt",
    hue="year",
    order=[season for season in SEASON_ORDER if season in selected_seasons],
    hue_order=sorted(season_summary["year"].unique()),
    ax=ax0,
)
ax0.set_xlabel("Musim")
ax0.set_ylabel("Rata-rata penyewaan per hari")
ax0.set_title("Rata-rata penyewaan harian per musim dan tahun")
sns.despine(ax=ax0)
st.pyplot(fig0)
plt.close(fig0)
st.caption(
    "Jumlah penyewaan per jam dijumlahkan per tanggal, lalu dirata-ratakan per hari."
)

st.divider()
st.subheader("Heatmap penyewaan berdasarkan hari dan jam")
st.caption(
    "Warna menunjukkan rata-rata penyewaan per jam pada hari dalam minggu yang dipilih. "
    "Hari dan jam tanpa observasi pada filter aktif ditampilkan kosong."
)
hourly_heatmap = (
    main_df.groupby(["weekday", "hr"])["cnt"]
    .mean()
    .unstack("hr")
    .reindex(index=range(7), columns=range(24))
)
hourly_heatmap.index = WEEKDAY_ORDER
fig_heatmap, ax_heatmap = plt.subplots(figsize=(14, 4.5))
sns.heatmap(
    hourly_heatmap,
    cmap="YlGnBu",
    linewidths=0.3,
    linecolor="white",
    cbar_kws={"label": "Rata-rata penyewaan per jam"},
    ax=ax_heatmap,
)
ax_heatmap.set_xlabel("Jam")
ax_heatmap.set_ylabel("Hari")
ax_heatmap.set_xticks(
    [hour + 0.5 for hour in range(24)],
    [f"{hour:02d}:00" for hour in range(24)],
    rotation=0,
)
sns.despine(ax=ax_heatmap, left=True, bottom=True)
st.pyplot(fig_heatmap)
plt.close(fig_heatmap)

st.divider()
st.subheader("1. Perbandingan penyewaan pada jam sibuk hari kerja")
st.caption(
    "Pilih musim Fall untuk mereplikasi pertanyaan bisnis proyek. "
    "Filter tanggal dan musim diterapkan pada grafik ini maupun grafik lainnya."
)

q1_df = main_df.loc[
    (main_df["workingday"] == 1) & main_df["hr"].isin([8, 17])
]
q1_summary = q1_df.groupby(["year", "hr"], as_index=False)["cnt"].mean()
growth_by_hour = {}

if q1_summary.empty:
    st.info("Tidak ada data jam sibuk hari kerja pada filter yang dipilih.")
else:
    q1_pivot = q1_summary.pivot(index="hr", columns="year", values="cnt")
    comparable_hours = [
        hour
        for hour in (8, 17)
        if hour in q1_pivot.index
        if 2011 in q1_pivot.columns
        and 2012 in q1_pivot.columns
        and pd.notna(q1_pivot.loc[hour, 2011])
        and pd.notna(q1_pivot.loc[hour, 2012])
        and q1_pivot.loc[hour, 2011] != 0
    ]
    if comparable_hours:
        growth_columns = st.columns(len(comparable_hours))
        for column, hour in zip(growth_columns, comparable_hours):
            growth = (
                q1_pivot.loc[hour, 2012] - q1_pivot.loc[hour, 2011]
            ) / q1_pivot.loc[hour, 2011] * 100
            growth_by_hour[hour] = growth
            column.metric(f"Kenaikan pukul {hour:02d}:00", f"{growth:+.2f}%")
    else:
        st.info("Pilih periode yang mencakup data 2011 dan 2012 untuk melihat persentase kenaikan.")

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    year_order = sorted(q1_summary["year"].unique())
    year_palette = {2011: "#7FB3D5", 2012: "#1F618D"}
    sns.barplot(
        data=q1_summary,
        x="hr",
        y="cnt",
        hue="year",
        order=[8, 17],
        hue_order=year_order,
        palette=year_palette,
        ax=ax1,
    )
    for container in ax1.containers:
        ax1.bar_label(container, fmt="%.1f", padding=3, fontweight="bold")
    ax1.set_xlabel("Jam operasional")
    ax1.set_xticks([0, 1], ["08:00", "17:00"])
    ax1.set_ylabel("Rata-rata penyewaan per jam")
    ax1.margins(y=0.15)
    sns.despine(ax=ax1)
    st.pyplot(fig1)
    plt.close(fig1)

st.divider()
st.subheader("2. Hubungan cuaca dengan pengguna kasual pada akhir pekan/libur")
q2_df = main_df.loc[main_df["workingday"] == 0].copy()

if q2_df.empty:
    st.info("Tidak ada data akhir pekan atau hari libur pada filter yang dipilih.")
else:
    correlation = (
        q2_df[list(WEATHER_LABELS) + ["casual"]]
        .corr()["casual"]
        .drop("casual")
        .dropna()
        .sort_values()
    )
    if correlation.empty:
        st.info("Data yang dipilih belum cukup untuk menghitung korelasi cuaca.")
    else:
        negative_correlations = correlation[correlation < 0]
        if not negative_correlations.empty:
            strongest_factor = negative_correlations.idxmin()
            st.metric(
                "Korelasi negatif terkuat dengan pengguna kasual",
                WEATHER_LABELS[strongest_factor],
                f"r = {negative_correlations.min():.2f}",
            )
        else:
            st.info("Tidak ditemukan korelasi negatif pada faktor cuaca di filter ini.")

        correlation_columns = st.columns([1, 1.2])
        with correlation_columns[0]:
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            labels = [WEATHER_LABELS[feature] for feature in correlation.index]
            colors = ["#C0392B" if value < 0 else "#2874A6" for value in correlation]
            bars = ax2.barh(labels, correlation.values, color=colors)
            ax2.axvline(0, color="black", linewidth=0.8)
            ax2.set_xlim(-1.15, 1.15)
            ax2.set_xlabel("Korelasi dengan jumlah pengguna kasual (r)")
            ax2.set_ylabel("")
            for bar, value in zip(bars, correlation.values):
                offset = 0.03 if value >= 0 else -0.03
                ax2.text(
                    value + offset,
                    bar.get_y() + bar.get_height() / 2,
                    f"{value:.2f}",
                    va="center",
                    ha="left" if value >= 0 else "right",
                )
            sns.despine(ax=ax2)
            st.pyplot(fig2)
            plt.close(fig2)

        with correlation_columns[1]:
            fig3, ax3 = plt.subplots(figsize=(7, 4))
            if q2_df["hum_pct"].nunique() > 1 and q2_df["casual"].nunique() > 1:
                sns.regplot(
                    data=q2_df,
                    x="hum_pct",
                    y="casual",
                    scatter_kws={"alpha": 0.3},
                    line_kws={"color": "red"},
                    ax=ax3,
                )
            else:
                sns.scatterplot(data=q2_df, x="hum_pct", y="casual", ax=ax3)
            ax3.set_xlabel("Kelembapan udara (%)")
            ax3.set_ylabel("Jumlah pengguna kasual")
            sns.despine(ax=ax3)
            st.pyplot(fig3)
            plt.close(fig3)

st.divider()
st.subheader("3. Pola penyewaan berdasarkan klaster waktu")

def categorize_time(hour):
    if 0 <= hour <= 5:
        return TIME_CLUSTER_ORDER[0]
    if 6 <= hour <= 9:
        return TIME_CLUSTER_ORDER[1]
    if 10 <= hour <= 15:
        return TIME_CLUSTER_ORDER[2]
    if 16 <= hour <= 19:
        return TIME_CLUSTER_ORDER[3]
    return TIME_CLUSTER_ORDER[4]


cluster_df = main_df.copy()
cluster_df["time_cluster"] = cluster_df["hr"].apply(categorize_time)
cluster_df["day_type"] = cluster_df["workingday"].map(
    {0: "Akhir Pekan/Libur", 1: "Hari Kerja"}
)
cluster_summary = (
    cluster_df.groupby(["time_cluster", "day_type"], as_index=False)[
        ["casual", "registered"]
    ]
    .mean()
)
cluster_melt = cluster_summary.melt(
    id_vars=["time_cluster", "day_type"],
    value_vars=["casual", "registered"],
    var_name="Tipe pengguna",
    value_name="Rata-rata penyewaan",
)

fig4 = sns.catplot(
    data=cluster_melt,
    x="time_cluster",
    y="Rata-rata penyewaan",
    hue="Tipe pengguna",
    col="day_type",
    col_order=["Akhir Pekan/Libur", "Hari Kerja"],
    order=TIME_CLUSTER_ORDER,
    kind="bar",
    height=5,
    aspect=1.2,
    palette=["#F39C12", "#2C3E50"],
)
fig4.set_titles("{col_name}", fontweight="bold")
fig4.set_axis_labels("Klaster waktu", "Rata-rata penyewaan")
fig4.tick_params(axis="x", rotation=20)
st.pyplot(fig4.fig)
plt.close(fig4.fig)

st.divider()
st.subheader("Kesimpulan dan tindak lanjut")
recommendations = []
for hour, growth in sorted(growth_by_hour.items()):
    direction = "naik" if growth >= 0 else "turun"
    recommendations.append(
        f"Pada pukul {hour:02d}:00, rata-rata penyewaan {direction} "
        f"{abs(growth):.2f}% dari 2011 ke 2012 pada filter aktif. "
        "Gunakan perubahan ini untuk mengevaluasi kebutuhan armada di jam tersebut."
    )

if not q2_df.empty:
    weather_correlation = (
        q2_df[list(WEATHER_LABELS) + ["casual"]]
        .corr()["casual"]
        .drop("casual")
        .dropna()
    )
    negative_weather_correlation = weather_correlation[weather_correlation < 0]
    if not negative_weather_correlation.empty:
        feature = negative_weather_correlation.idxmin()
        recommendations.append(
            f"{WEATHER_LABELS[feature]} memiliki korelasi negatif terkuat "
            f"dengan pengguna kasual (r = {negative_weather_correlation[feature]:.2f}) "
            "pada akhir pekan/libur. Uji promosi yang relevan dan ukur dampaknya; "
            "korelasi ini tidak membuktikan hubungan sebab-akibat."
        )

if not cluster_summary.empty:
    weekend_casual = cluster_summary.loc[
        cluster_summary["day_type"] == "Akhir Pekan/Libur"
    ]
    if not weekend_casual.empty:
        peak = weekend_casual.loc[weekend_casual["casual"].idxmax()]
        recommendations.append(
            f"Pengguna kasual akhir pekan/libur paling ramai pada "
            f"{peak['time_cluster'].split('. ', 1)[-1].lower()} "
            f"(rata-rata {peak['casual']:.1f} penyewaan per jam). "
            "Pertimbangkan penempatan sepeda dan promosi pada periode tersebut."
        )

if recommendations:
    for recommendation in recommendations:
        st.markdown(f"- {recommendation}")
else:
    st.info("Belum cukup data pada filter aktif untuk menyusun tindak lanjut.")
