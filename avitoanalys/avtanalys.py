import pandas as pd
import numpy as np



df = pd.read_excel("iphone13_avito.xlsx")


print("Исходные данные:")
print(df.head())
print("\n")



df["Цена_числа"] = pd.to_numeric(
    df["Цена"]
    .astype(str)
    .str.replace("₽", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.replace(",", ".", regex=False),
    errors="coerce"
)



df_clean = df.dropna(subset=["Цена_числа"])


print(f"Объявлений с корректной ценой: {len(df_clean)} из {len(df)}")
print("\n")




avg_price = df_clean["Цена_числа"].mean()

print(f"Средняя цена: {avg_price:.0f} ₽")




min_price = df_clean["Цена_числа"].min()
max_price = df_clean["Цена_числа"].max()


print(
    f"Минимум: {min_price:.0f} ₽, "
    f"Максимум: {max_price:.0f} ₽"
)

print("\n")




top_10_expensive = (
    df_clean
    .sort_values(
        by="Цена_числа",
        ascending=False
    )
    .head(10)
)


print("ТОП-10 самых дорогих:")
print(top_10_expensive[[
    "Название",
    "Цена",
    "Город",
    "Ссылка"
]])

print("\n")




top_10_cheap = (
    df_clean
    .sort_values(
        by="Цена_числа",
        ascending=True
    )
    .head(10)
)


print("ТОП-10 самых дешёвых:")
print(top_10_cheap[[
    "Название",
    "Цена",
    "Город",
    "Ссылка"
]])

print("\n")




by_city = (
    df_clean
    .groupby("Город")
    .agg(
        Количество=("Цена_числа", "count"),
        Средняя_цена=("Цена_числа", "mean")
    )
    .sort_values(
        by="Количество",
        ascending=False
    )
)


print("Распределение по городам:")
print(by_city)




median_price = df_clean["Цена_числа"].median()

print("\nМедианная цена:")
print(f"{median_price:.0f} ₽")




with pd.ExcelWriter(
    "iphone13_analysis.xlsx",
    engine="openpyxl"
) as writer:

    df_clean.to_excel(
        writer,
        sheet_name="Все объявления",
        index=False
    )

    top_10_expensive.to_excel(
        writer,
        sheet_name="Top 10 Дорогие",
        index=False
    )

    top_10_cheap.to_excel(
        writer,
        sheet_name="Top 10 Дешёвые",
        index=False
    )

    by_city.to_excel(
        writer,
        sheet_name="По городам"
    )


print("\nАнализ завершён!")
print("Файл сохранён: iphone13_analysis.xlsx")