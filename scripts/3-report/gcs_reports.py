#!/usr/bin/env python
"""
This file is dedicated to visualizing and analyzing the data collected
from Google Custom Search.
"""
# Standard library
import argparse
import os
import sys
import traceback
from datetime import datetime, timezone

# Third-party
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
from pandas import PeriodIndex

# Add parent directory so shared can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# First-party/Local
import shared  # noqa: E402

# Setup
LOGGER, PATHS = shared.setup(__file__)


def parse_arguments():
    """
    Parses command-line arguments, returns parsed arguments.
    """
    LOGGER.info("Parsing command-line arguments")

    # Taken from shared module, fix later
    datetime_today = datetime.now(timezone.utc)
    quarter = PeriodIndex([datetime_today.date()], freq="Q")[0]

    parser = argparse.ArgumentParser(description="Google Custom Search Report")
    parser.add_argument(
        "--quarter",
        "-q",
        type=str,
        default=f"{quarter}",
        help="Data quarter in format YYYYQx, e.g., 2024Q2",
    )
    parser.add_argument(
        "--skip-commit",
        action="store_true",
        help="Don't git commit changes (also skips git push changes)",
    )
    parser.add_argument(
        "--skip-push",
        action="store_true",
        help="Don't git push changes",
    )
    parser.add_argument(
        "--show-plots",
        action="store_true",
        help="Show generated plots (in addition to saving them)",
    )
    args = parser.parse_args()
    if args.skip_commit:
        args.skip_push = True
    return args


def load_data(args):
    """
    Load the collected data from the CSV file.
    """
    selected_quarter = args.quarter

    file_path = os.path.join(
        PATHS["data"], f"{selected_quarter}", "1-fetch", "gcs_fetched.csv"
    )

    if not os.path.exists(file_path):
        LOGGER.error(f"Data file not found: {file_path}")
        return pd.DataFrame()

    data = pd.read_csv(file_path)
    LOGGER.info(f"Data loaded from {file_path}")
    return data


def visualize_by_country(data, args):
    """
    Create a bar chart for the number of webpages licensed by country.
    """
    LOGGER.info(
        "Creating a bar chart for the number of webpages licensed by country."
    )

    selected_quarter = args.quarter

    # Get the list of country columns dynamically
    columns = [col.strip() for col in data.columns.tolist()]

    start_index = columns.index("United States")
    end_index = columns.index("Japan") + 1

    countries = columns[start_index:end_index]

    data.columns = data.columns.str.strip()

    LOGGER.info(f"Cleaned Columns: {data.columns.tolist()}")

    # Aggregate the data by summing the counts for each country
    country_data = data[countries].sum()

    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x=country_data.index, y=country_data.values)
    plt.title(
        f"Number of Google Webpages Licensed by Country ({selected_quarter})"
    )
    plt.xlabel("Country")
    plt.ylabel("Number of Webpages")
    plt.xticks(rotation=45)

    # Add value numbers to the top of each bar
    for p in ax.patches:
        ax.annotate(
            format(p.get_height(), ",.0f"),
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="center",
            xytext=(0, 9),
            textcoords="offset points",
        )

    # Format the y-axis to display numbers without scientific notation
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)))
    )

    output_directory = os.path.join(
        PATHS["data"], f"{selected_quarter}", "3-report"
    )

    LOGGER.info(f"Output directory: {output_directory}")

    # Create the directory if it does not exist
    os.makedirs(output_directory, exist_ok=True)
    image_path = os.path.join(output_directory, "gcs_country_report.png")
    plt.savefig(image_path)

    if args.show_plots:
        plt.show()

    shared.update_readme(
        PATHS,
        image_path,
        "Google Custom Search",
        "Number of Google Webpages Licensed by Country",
        "Country Report",
        args,
    )

    LOGGER.info("Visualization by country created.")


def visualize_by_license_type(data, args):
    """
    Create a bar chart for the number of webpages licensed by license type
    """
    LOGGER.info(
        "Creating a bar chart for the number of "
        "webpages licensed by license type."
    )

    selected_quarter = args.quarter

    # Strip any leading/trailing spaces from the columns
    data.columns = data.columns.str.strip()

    # Sum the values across all columns except the first one ('LICENSE TYPE')
    license_data = data.set_index("LICENSE TYPE").sum(axis=1)

    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x=license_data.index, y=license_data.values)
    plt.title(
        f"Number of Webpages Licensed by License Type ({selected_quarter})"
    )
    plt.xlabel("License Type")
    plt.ylabel("Number of Webpages")
    plt.xticks(rotation=45, ha="right")

    # Use shorter X axis labels
    ax.set_xticklabels(
        [
            "CC BY 2.5" if "by/2.5" in label else label
            for label in license_data.index
        ]
    )

    # Use the millions formatter for y-axis
    def millions_formatter(x, pos):
        "The two args are the value and tick position"
        return f"{x * 1e-6:.1f}M"

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))

    plt.tight_layout()

    output_directory = os.path.join(
        PATHS["data"], f"{selected_quarter}", "3-report"
    )

    LOGGER.info(f"Output directory: {output_directory}")

    # Create the directory if it does not exist
    os.makedirs(output_directory, exist_ok=True)
    image_path = os.path.join(output_directory, "gcs_licensetype_report.png")

    plt.savefig(image_path)

    if args.show_plots:
        plt.show()

    shared.update_readme(
        PATHS,
        image_path,
        "Google Custom Search",
        "Number of Webpages Licensed by License Type",
        "License Type Report",
        args,
    )

    LOGGER.info("Visualization by license type created.")


def visualize_by_language(data, args):
    """
    Create a bar chart for the number of webpages licensed by language.
    """
    LOGGER.info(
        "Creating a bar chart for the number of webpages licensed by language."
    )

    selected_quarter = args.quarter

    # Get the list of country columns dynamically
    columns = [col.strip() for col in data.columns.tolist()]

    start_index = columns.index("English")
    end_index = columns.index("Indonesian") + 1

    languages = columns[start_index:end_index]

    data.columns = data.columns.str.strip()

    LOGGER.info(f"Cleaned Columns: {data.columns.tolist()}")

    # Aggregate the data by summing the counts for each country
    language_data = data[languages].sum()

    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x=language_data.index, y=language_data.values)
    plt.title(
        f"Number of Google Webpages Licensed by Language ({selected_quarter})"
    )
    plt.xlabel("Language")
    plt.ylabel("Number of Webpages")
    plt.xticks(rotation=45)

    # Add value numbers to the top of each bar
    for p in ax.patches:
        ax.annotate(
            format(p.get_height(), ",.0f"),
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="center",
            xytext=(0, 9),
            textcoords="offset points",
        )

    # Format the y-axis to display numbers without scientific notation
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)))
    )

    output_directory = os.path.join(
        PATHS["data"], f"{selected_quarter}", "3-report"
    )

    LOGGER.info(f"Output directory: {output_directory}")

    # Create the directory if it does not exist
    os.makedirs(output_directory, exist_ok=True)
    image_path = os.path.join(output_directory, "gcs_language_report.png")
    plt.savefig(image_path)

    if args.show_plots:
        plt.show()

    shared.update_readme(
        PATHS,
        image_path,
        "Google Custom Search",
        "Number of Google Webpages Licensed by Language",
        "Language Report",
        args,
    )

    LOGGER.info("Visualization by language created.")


def main():

    # Fetch and merge changes
    shared.fetch_and_merge(PATHS["repo"])

    args = parse_arguments()

    data = load_data(args)
    if data.empty:
        return

    current_directory = os.getcwd()
    LOGGER.info(f"Current working directory: {current_directory}")

    visualize_by_country(data, args)
    visualize_by_license_type(data, args)
    visualize_by_language(data, args)

    # Add and commit changes
    if not args.skip_commit:
        shared.add_and_commit(PATHS["repo"], "Added and committed new reports")

    # Push changes
    if not args.skip_push:
        shared.push_changes(PATHS["repo"])


if __name__ == "__main__":
    try:
        main()
    except shared.QuantifyingException as e:
        if e.exit_code == 0:
            LOGGER.info(e.message)
        else:
            LOGGER.error(e.message)
        sys.exit(e.exit_code)
    except SystemExit as e:
        LOGGER.error(f"System exit with code: {e.code}")
        sys.exit(e.code)
    except KeyboardInterrupt:
        LOGGER.info("(130) Halted via KeyboardInterrupt.")
        sys.exit(130)
    except Exception:
        LOGGER.exception(f"(1) Unhandled exception: {traceback.format_exc()}")
        sys.exit(1)
