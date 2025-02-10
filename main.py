import pandas as pd
import pdfplumber
from sklearn.linear_model import LinearRegression


def extract_data_from_pdf(pdf_path):
    """
    Extract data from a PDF file.
    """
    extracted_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                table = table[1:]  # Drop the header row
                for row in table:
                    if len(row) < 4:  # Skip invalid rows
                        continue
                    try:
                        size = row[2]  # Assuming size is in column 3
                        color = row[3]  # Assuming color is in column 4
                        price_sroy = row[
                            5]  # Saga Royal average price in column 6
                        price_saga = row[8]  # Saga average price in column 9

                        extracted_data.append({
                            'size': size,
                            'color': color,
                            'price_sroy': price_sroy,
                            'price_saga': price_saga
                        })
                    except IndexError:
                        continue

    return extracted_data


def preprocess_data(data):
    """
    Preprocess extracted data into a cleaned DataFrame.
    """
    df = pd.DataFrame(data)

    # Remove rows where 'color' is empty
    df = df[df['color'] != '']

    # Clean up 'color' column
    df['color'] = df['color'].str.replace('\n', '')

    # Fill missing sizes forward
    df['size'] = pd.to_numeric(df['size'], errors='coerce').ffill()

    # Convert price columns to numeric
    for col in ['price_sroy', 'price_saga']:
        df[col] = pd.to_numeric(df[col].str.replace(',', '.', regex=False),
                                errors='coerce')

    return df


def get_entries_by_color(df):
    """
    Group DataFrame entries by color.
    """
    unique_colors = df['color'].unique()
    color_dfs = {
        color: df[df['color'] == color].copy()
        for color in unique_colors
    }
    return color_dfs


def extrapolate_prices(df):
    """
    Extrapolate prices for 'price_sroy' and 'price_saga' using a linear model.
    Only replaces NaN values with extrapolated values.
    """
    for column in ['price_sroy', 'price_saga']:
        # Select rows with valid (non-NaN) values
        valid_rows = df[df[column].notna()]
        if valid_rows.empty:
            continue  # Skip if no valid data exists for the column

        # Extract sizes and prices
        sizes = valid_rows['size'].values.reshape(-1, 1)
        prices = valid_rows[column].values

        # Fit a linear regression model
        model = LinearRegression().fit(sizes, prices)

        # Predict for all sizes
        predictions = model.predict(df['size'].values.reshape(-1, 1))

        # Apply predictions only to NaN values in the column
        df[f'extrapolated_{column}'] = df[column].combine_first(
            pd.Series(predictions, index=df.index))

        # Round the extrapolated values to 1 decimal place
        df[f'extrapolated_{column}'] = df[f'extrapolated_{column}'].round(1)

    return df


def main():
    # Path to your PDF file
    pdf_path = './import/sblueM JUN23.pdf'

    # Extract, preprocess, and group data by color
    raw_data = extract_data_from_pdf(pdf_path)
    df = preprocess_data(raw_data)
    print("Preprocessed DataFrame:\n", df.head(100))
    color_dfs = get_entries_by_color(df)

    # Extrapolate prices for each color group
    for color, color_df in color_dfs.items():
        color_dfs[color] = extrapolate_prices(color_df)
        print(f"Extrapolated prices for color '{color}':")

        # Safely print columns if they exist
        columns_to_print = ['size', 'price_sroy', 'price_saga']
        extrapolated_columns = [
            'extrapolated_price_sroy', 'extrapolated_price_saga'
        ]
        for col in extrapolated_columns:
            if col in color_df.columns:
                columns_to_print.append(col)

        print(color_df[columns_to_print])
        print("\n")


if __name__ == "__main__":
    main()
