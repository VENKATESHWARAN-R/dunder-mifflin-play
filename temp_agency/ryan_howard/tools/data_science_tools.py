import os
import random
from typing import List
import uuid
from typing import Optional

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from google.cloud import storage


class DataScienceTools:
    """
    DataScienceAgent encapsulates a DataFrame and provides methods for data loading,
    processing, analysis, and visualization. Each method returns a dictionary
    with concise information or file paths, enabling an LLM-based agent to
    interact without ingesting raw data directly.
    """

    def __init__(self):
        """
        Initialize the agent with no DataFrame loaded.
        """
        self.df = None

    def load_csv(
        self, file_path: str, drop_unnamed_index: Optional[bool] = None, **kwargs
    ) -> dict:
        """Load a CSV file into memory, supporting both local and GCS paths.

        If `file_path` starts with 'gs://', downloads from GCS to a temp file.

        Args:
            file_path (str): Local path or GCS URI (gs://bucket/path/file.csv).
            drop_unnamed_index (bool, optional): Drop 'Unnamed:' index columns. Defaults to True.
            **kwargs: Additional arguments passed to `pd.read_csv`.

        Returns:
            dict: status, row/column counts, dropped_columns list, or error message.
        """
        # Default for dropping unnamed index
        if drop_unnamed_index is None or drop_unnamed_index == "":
            drop_unnamed_index = True

        # Handle GCS URIs
        local_path = file_path
        if file_path.startswith("gs://"):
            download_res = self.read_file_from_gcs(file_path)
            if download_res.get("status") != "success":
                return {"status": "error", "message": download_res.get("message")}
            local_path = download_res["result"]["local_path"]

        try:
            # Read CSV from local path
            df = pd.read_csv(local_path, **kwargs)

            dropped_columns = []
            if drop_unnamed_index:
                # Identify columns like 'Unnamed: *'
                unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed:")]
                for col in unnamed_cols:
                    col_vals = df[col].dropna()
                    if (
                        len(col_vals) > 0
                        and pd.api.types.is_numeric_dtype(col_vals)
                        and (col_vals.astype(int) == col_vals).all()
                        and (
                            (col_vals.astype(int) == range(len(col_vals))).all()
                            or (
                                col_vals.astype(int) == range(1, len(col_vals) + 1)
                            ).all()
                        )
                    ):
                        df = df.drop(columns=[col])
                        dropped_columns.append(col)

            self.df = df
            result = {"status": "success", "rows": df.shape[0], "columns": df.shape[1]}
            if dropped_columns:
                result["dropped_columns"] = dropped_columns
            return result

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def read_file_from_gcs(self, gcs_path: str) -> dict:
        """
        Downloads a single file from GCS to /tmp and returns a dict with status, message, and result.

        Args:
            gcs_path (str): Full GCS path including filename, e.g. "gs://my-bucket/path/to/file.txt"

        Returns:
            Dict[str, Any]: {
                "status": "success"|"error",
                "message": str,
                "result": {
                    "local_path": str,
                    "gcs_path": str
                }
            }
        """
        try:
            if not gcs_path.startswith("gs://"):
                raise ValueError("GCS path must start with gs://")

            parts = gcs_path[5:].split("/", 1)
            bucket_name = parts[0]
            blob_path = parts[1]

            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)

            # Download to a temp file in /tmp
            local_dir = "/tmp"
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, os.path.basename(blob_path))
            blob.download_to_filename(local_path)

            return {
                "status": "success",
                "message": "Download completed",
                "result": {"local_path": local_path, "gcs_path": gcs_path},
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Download failed: {str(e)}",
                "result": {},
            }

    def upload_file_to_gcs(self, gcs_path: str, local_file_path: str) -> dict:
        """
        Uploads a local file to GCS and returns a dict with status, message, and result.

        Args:
            gcs_path (str): Full GCS path including target filename, e.g. "gs://my-bucket/path/to/upload.txt"
            local_file_path (str): Full local path to the file, e.g. "/tmp/upload.txt"

        Returns:
            Dict[str, Any]: {
                "status": "success"|"error",
                "message": str,
                "result": {
                    "local_path": str,
                    "gcs_path": str
                }
            }
        """
        try:
            if not gcs_path.startswith("gs://"):
                raise ValueError("GCS path must start with gs://")
            if not os.path.isfile(local_file_path):
                raise ValueError(f"Local file does not exist: {local_file_path}")

            parts = gcs_path[5:].split("/", 1)
            bucket_name = parts[0]
            blob_path = parts[1]

            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)

            blob.upload_from_filename(local_file_path)

            return {
                "status": "success",
                "message": "Upload completed",
                "result": {"local_path": local_file_path, "gcs_path": gcs_path},
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Upload failed: {str(e)}",
                "result": {},
            }

    def get_basic_info(self) -> dict:
        """Retrieve basic metadata about the loaded DataFrame: shape,
        column names, data types, and count of missing values per column.

        Returns:
            dict: {
                'shape': [rows, columns],
                'columns': [list of column names],
                'dtypes': {column: dtype, ...},
                'missing_values': {column: missing_count, ...}
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}
        info = {
            "shape": list(self.df.shape),
            "columns": self.df.columns.tolist(),
            "dtypes": self.df.dtypes.astype(str).to_dict(),
            "missing_values": self.df.isnull().sum().to_dict(),
        }
        return info

    def get_summary_statistics(
        self, include_categorical: Optional[bool] = None
    ) -> dict:
        """Compute summary statistics for numerical columns, optionally including categorical.

        Args:
            include_categorical (bool, optional): If True or empty string, include all columns; otherwise only numeric.
                                             Default is False if None or empty string is provided.

        Returns:
            dict: Nested dictionary of summary statistics: {column: {stat: value, ...}, ...}
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Set default value if None or empty string
        if include_categorical is None or include_categorical == "":
            include_categorical = False

        if include_categorical:
            summary = self.df.describe(include="all")
        else:
            summary = self.df.describe()

        # Convert to regular dictionary and replace NaN values with None
        result_dict = summary.to_dict()
        for col in result_dict:
            for stat in result_dict[col]:
                if pd.isna(result_dict[col][stat]):
                    result_dict[col][stat] = None

        return result_dict

    def plot_histograms(
        self,
        columns: Optional[str] = None,
        bins: Optional[int] = None,
        fig_height: Optional[int] = None,
        fig_width: Optional[int] = None,
    ) -> dict:
        """Generate and save histograms for numeric columns.

        Args:
            columns (str, optional): Comma-separated column names to plot; if None or empty string, use all numeric columns.
            bins (int, optional): Number of bins for histograms. Default is 30 if None or empty string is provided.
            fig_height (int, optional): Height of the figure in inches. Default is 6 if None or empty string is provided.
            fig_width (int, optional): Width of the figure in inches. Default is 12 if None or empty string is provided.

        Returns:
            dict: {
                'file_path': path to the saved PNG image,
                'type': 'image',
                'columns_plotted': list of columns plotted,
                'description': brief description of the plot
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Set default values if None or empty string
        if bins is None or bins == "":
            bins = 30
        if fig_height is None or fig_height == "":
            fig_height = 6
        if fig_width is None or fig_width == "":
            fig_width = 12

        if columns is None or columns == "":
            columns_list = self.df.select_dtypes(include=np.number).columns.tolist()
        else:
            columns_list = [col.strip() for col in columns.split(",") if col.strip()]

        if columns_list is None:
            columns_list = []
        num_cols = len(columns_list)
        if num_cols == 0:
            return {"status": "error", "message": "No numerical columns to plot."}

        fig, axes = plt.subplots(
            nrows=(num_cols + 2) // 3, ncols=3, figsize=(fig_width, fig_height)
        )
        axes = axes.flatten()
        for idx, col in enumerate(columns_list):
            self.df[col].hist(bins=bins, ax=axes[idx])
            axes[idx].set_title(col)
        # Safely remove unused axes
        for j in range(len(columns_list), len(axes)):
            fig.delaxes(axes[j])
        plt.tight_layout()
        filename = f"histograms_{uuid.uuid4().hex}.png"
        plt.savefig(filename)
        plt.close()
        return {
            "file_path": os.path.abspath(filename),
            "type": "image",
            "columns_plotted": columns_list,
            "description": "Histograms for numeric columns",
        }

    def get_unique_values(self, column: str) -> dict:
        """Retrieve unique values from a specified column.
        If there are more than 50 unique values,
        randomly sample 50 of them to return.

        Args:
            column (str): Name of the column to inspect.

        Returns:
            dict: {
                'unique_values': [list of unique values] or error message
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}
        if column not in self.df.columns:
            return {"status": "error", "message": f"Column '{column}' not found."}

        # Get unique values
        unique_vals = self.df[column].unique()

        # Convert to Python native types and handle special values
        processed_vals = []
        for val in unique_vals:
            if pd.isna(val):  # Handle NaN, None values
                processed_vals.append(None)
            elif isinstance(val, (np.integer, np.floating, np.bool_)):
                # Convert numpy types to native Python types
                processed_vals.append(val.item())
            else:
                # Other values (strings, lists, etc.) should already be in native Python format
                processed_vals.append(val)

        # Sample if there are too many unique values
        if len(processed_vals) > 50:
            processed_vals = random.sample(
                processed_vals, 50
            )  # Limit to 50 unique values

        return {"unique_values": processed_vals}

    def get_data_sample(self, n: Optional[int] = None) -> dict:
        """Retrieve a random sample of n rows with their column names from the DataFrame.

        Args:
            n (int, optional): Number of rows to sample. Default is 5 if None or empty string is provided.

        Returns:
            dict: {
                'sample': [list of sampled rows] or error message
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Set default value if None or empty string
        if n is None or n == "":
            n = 5

        # Get the sample data as records
        sample = self.df.sample(n=n).to_dict(orient="records")

        # Replace NaN values with None for JSON serialization
        for record in sample:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                # Convert numpy types to native Python types for JSON serialization
                elif isinstance(value, (np.integer, np.floating, np.bool_)):
                    record[key] = value.item()

        return {"sample": sample}

    def create_scatter_plot(
        self,
        x_column: str,
        y_column: str,
        color_column: Optional[str] = None,
        fig_height: Optional[int] = None,
        fig_width: Optional[int] = None,
    ) -> dict:
        """Create a scatter plot between two numerical columns, optionally colored by a third column.

        Args:
            x_column (str): Name of the column to plot on the x-axis.
            y_column (str): Name of the column to plot on the y-axis.
            color_column (str, optional): Name of the column to use for coloring points. If None or empty string, no coloring is applied.
            fig_height (int, optional): Height of the figure in inches. Default is 8 if None or empty string is provided.
            fig_width (int, optional): Width of the figure in inches. Default is 10 if None or empty string is provided.

        Returns:
            dict: {
                'file_path': path to the saved PNG image,
                'type': 'image',
                'description': brief description of the plot
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Set default values if None or empty string
        if fig_height is None or fig_height == "":
            fig_height = 8
        if fig_width is None or fig_width == "":
            fig_width = 10

        # Treat empty string as None for color_column
        if color_column == "":
            color_column = None

        if x_column not in self.df.columns:
            return {"status": "error", "message": f"Column '{x_column}' not found."}

        if y_column not in self.df.columns:
            return {"status": "error", "message": f"Column '{y_column}' not found."}

        if color_column is not None and color_column not in self.df.columns:
            return {"status": "error", "message": f"Column '{color_column}' not found."}

        plt.figure(figsize=(fig_width, fig_height))

        if color_column:
            plt.scatter(
                self.df[x_column],
                self.df[y_column],
                c=self.df[color_column].astype("category").cat.codes
                if self.df[color_column].dtype == "object"
                else self.df[color_column],
                alpha=0.6,
                cmap="viridis",
            )
            if self.df[color_column].dtype == "object":
                # Create a legend for categorical data
                categories = self.df[color_column].astype("category").cat.categories
                from matplotlib.lines import Line2D

                handles = [
                    Line2D(
                        [0],
                        [0],
                        marker="o",
                        color="w",
                        markerfacecolor="C" + str(i % 10),
                        markersize=10,
                    )
                    for i in range(len(categories))
                ]
                plt.legend(handles, categories, title=color_column, loc="best")
            else:
                # Add a colorbar for numerical data
                plt.colorbar(label=color_column)
        else:
            plt.scatter(self.df[x_column], self.df[y_column], alpha=0.6)

        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f"Scatter plot of {y_column} vs {x_column}")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        filename = f"scatter_{x_column}_{y_column}_{uuid.uuid4().hex}.png"
        plt.savefig(filename)
        plt.close()

        return {
            "file_path": os.path.abspath(filename),
            "type": "image",
            "description": f"Scatter plot showing relationship between {x_column} and {y_column}"
            + (f", colored by {color_column}" if color_column else ""),
        }

    def plot_correlation_heatmap(
        self, fig_width: Optional[int] = None, fig_height: Optional[int] = None
    ) -> dict:
        """Create a correlation heatmap for all numerical columns.

        Args:
            fig_width (int, optional): Width of the figure in inches. Default is 10 if None or empty string is provided.
            fig_height (int, optional): Height of the figure in inches. Default is 8 if None or empty string is provided.

        Returns:
            dict: {
                'file_path': path to the saved PNG image,
                'type': 'image',
                'description': description of the heatmap
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Set default values if None or empty string
        if fig_width is None or fig_width == "":
            fig_width = 10
        if fig_height is None or fig_height == "":
            fig_height = 8

        # Get only numeric columns
        numeric_df = self.df.select_dtypes(include=np.number)

        if numeric_df.shape[1] < 2:
            return {
                "status": "error",
                "message": "At least two numeric columns are required for a correlation matrix.",
            }

        # Calculate correlation and ensure float type
        corr_matrix = numeric_df.corr().astype(float)

        # Create the heatmap
        plt.figure(figsize=(fig_width, fig_height))
        plt.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)

        # Add correlation values as text
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                cell = corr_matrix.iloc[i, j]
                if isinstance(cell, complex):
                    value = float(cell.real)
                elif isinstance(cell, (int, float, np.integer, np.floating)):
                    value = float(cell)
                else:
                    # For unsupported types (e.g., str, date), skip annotation or convert to string
                    value = None
                text_color = (
                    "white" if (value is not None and abs(value) > 0.65) else "black"
                )
                plt.text(
                    j,
                    i,
                    f"{value:.2f}" if value is not None else "",
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=8,
                )

        # Styling
        plt.colorbar(label="Correlation Coefficient")
        plt.title("Correlation Matrix Heatmap")
        plt.xticks(
            range(len(corr_matrix.columns)),
            list(map(str, corr_matrix.columns)),
            rotation=45,
            ha="right",
        )
        plt.yticks(range(len(corr_matrix.columns)), list(map(str, corr_matrix.columns)))
        plt.tight_layout()

        # Save
        filename = f"correlation_heatmap_{uuid.uuid4().hex}.png"
        plt.savefig(filename)
        plt.close()

        # Convert column names to a list of strings to ensure basic Python types
        column_names = [str(col) for col in numeric_df.columns.tolist()]

        return {
            "file_path": os.path.abspath(filename),
            "type": "image",
            "columns": column_names,
            "description": f"Correlation heatmap for {len(column_names)} numerical columns",
        }

    def create_boxplot(
        self,
        columns: Optional[str] = None,
        fig_width: Optional[int] = None,
        fig_height: Optional[int] = None,
    ) -> dict:
        """Create box plots for specified columns to visualize distributions and outliers.

        Args:
            columns (str, optional): Comma-separated column names to plot; if None or empty string, use all numeric columns.
            fig_width (int, optional): Width of the figure in inches. Default is 12 if None or empty string is provided.
            fig_height (int, optional): Height of the figure in inches. Default is 6 if None or empty string is provided.

        Returns:
            dict: {
                'file_path': path to the saved PNG image,
                'type': 'image',
                'columns_plotted': list of columns plotted,
                'description': description of the plot
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Set default values if None or empty string
        if fig_width is None or fig_width == "":
            fig_width = 12
        if fig_height is None or fig_height == "":
            fig_height = 6

        if columns is None or columns == "":
            columns_list = self.df.select_dtypes(include=np.number).columns.tolist()
        else:
            columns_list = [col.strip() for col in columns.split(",") if col.strip()]

        if not columns_list:
            return {"status": "error", "message": "No numerical columns to plot."}

        # Verify all columns exist in the dataframe
        missing_columns = [col for col in columns_list if col not in self.df.columns]
        if missing_columns:
            return {
                "status": "error",
                "message": f"Columns not found: {', '.join(missing_columns)}",
            }

        # Create the boxplots
        plt.figure(figsize=(fig_width, fig_height))
        self.df[columns_list].boxplot(vert=True, patch_artist=True)
        plt.title("Box Plot of Selected Columns")
        plt.xticks(rotation=45, ha="right")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Save
        filename = f"boxplot_{uuid.uuid4().hex}.png"
        plt.savefig(filename)
        plt.close()

        # Convert column names to strings to ensure basic Python types
        columns_str = [str(col) for col in columns_list]

        return {
            "file_path": os.path.abspath(filename),
            "type": "image",
            "columns_plotted": columns_str,
            "description": f"Box plot showing distribution and outliers for {len(columns_str)} numerical columns",
        }

    def plot_pie_chart(
        self,
        column: str,
        max_categories: Optional[int] = None,
        fig_width: Optional[int] = None,
        fig_height: Optional[int] = None,
    ) -> dict:
        """Create a pie chart for a categorical column.

        Args:
            column (str): The categorical column to plot.
            max_categories (int, optional): Maximum number of categories to include before grouping as 'Other'. Default is 10 if None or empty string is provided.
            fig_width (int, optional): Width of the figure in inches. Default is 10 if None or empty string is provided.
            fig_height (int, optional): Height of the figure in inches. Default is 8 if None or empty string is provided.

        Returns:
            dict: {
                'file_path': path to the saved PNG image,
                'type': 'image',
                'description': description of the pie chart
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Set default values if None or empty string
        if max_categories is None or max_categories == "":
            max_categories = 10
        if fig_width is None or fig_width == "":
            fig_width = 10
        if fig_height is None or fig_height == "":
            fig_height = 8

        if column not in self.df.columns:
            return {"status": "error", "message": f"Column '{column}' not found."}

        # Get value counts
        value_counts = self.df[column].value_counts()

        # Handle NaN values in the counts
        if pd.isna(value_counts.index).any():
            # Create a new index without NaN values
            new_index = [
                str(idx) if not pd.isna(idx) else "Missing/NaN"
                for idx in value_counts.index
            ]
            value_counts.index = pd.Index(new_index)

        # Group smaller categories
        if len(value_counts) > max_categories:
            top_n = value_counts.nlargest(max_categories - 1)
            others = pd.Series({"Other": value_counts.drop(top_n.index).sum()})
            value_counts = pd.concat([top_n, others])

        # Convert to lists for pie chart
        labels = [str(label) for label in value_counts.index]
        values = value_counts.values.tolist()

        # Create the pie chart
        plt.figure(figsize=(fig_width, fig_height))
        plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            shadow=True,
            explode=[0.05] * len(values),  # Slight separation for all slices
        )
        plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(f"Distribution of {column}")
        plt.tight_layout()

        # Save
        filename = f"pie_chart_{column}_{uuid.uuid4().hex}.png"
        plt.savefig(filename)
        plt.close()

        return {
            "file_path": os.path.abspath(filename),
            "type": "image",
            "column": column,
            "categories": labels,
            "description": f"Pie chart showing distribution of {column} across {len(value_counts)} categories",
        }

    def modify_dataset(
        self,
        drop_columns: Optional[str] = None,
        set_index: Optional[str] = None,
        datetime_columns: Optional[str] = None,
        datetime_format: Optional[str] = None,
        fill_na: Optional[str] = None,
        fill_value: Optional[str] = None,
    ) -> dict:
        """Modify the dataset by dropping columns, setting index, converting datetime columns, or filling missing values.

        Args:
            drop_columns (str, optional): Comma-separated names of columns to drop. Empty string is treated as None.
            set_index (str, optional): Name of the column to set as index. Empty string is treated as None.
            datetime_columns (str, optional): Comma-separated names of columns to convert to datetime. Empty string is treated as None.
            datetime_format (str, optional): Format string for datetime conversion (e.g., '%Y-%m-%d'). Empty string is treated as None.
            fill_na (str, optional): Comma-separated names of columns to fill NA values in. Empty string is treated as None.
            fill_value (str, optional): Value to use for filling NA values (use 'mean', 'median', 'mode', or a specific value). Empty string is treated as None.

        Returns:
            dict: {
                'status': 'success' or 'error',
                'message': description of changes made,
                'shape': new shape of the dataset after modifications
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Treat empty strings as None
        if drop_columns == "":
            drop_columns = None
        if set_index == "":
            set_index = None
        if datetime_columns == "":
            datetime_columns = None
        if datetime_format == "":
            datetime_format = None
        if fill_na == "":
            fill_na = None
        if fill_value == "":
            fill_value = None

        modifications = []

        # Drop columns if specified
        if drop_columns:
            columns_to_drop = [col.strip() for col in drop_columns.split(",")]
            # Check if all columns exist
            invalid_columns = [
                col for col in columns_to_drop if col not in self.df.columns
            ]
            if invalid_columns:
                return {
                    "status": "error",
                    "message": f"Columns not found: {', '.join(invalid_columns)}",
                }

            self.df = self.df.drop(columns=columns_to_drop)
            modifications.append(f"Dropped columns: {', '.join(columns_to_drop)}")

        # Set index if specified
        if set_index:
            if set_index not in self.df.columns:
                return {
                    "status": "error",
                    "message": f"Column '{set_index}' not found for setting as index.",
                }

            self.df = self.df.set_index(set_index)
            modifications.append(f"Set '{set_index}' as index")

        # Convert datetime columns if specified
        if datetime_columns:
            dt_columns = [col.strip() for col in datetime_columns.split(",")]
            invalid_columns = [col for col in dt_columns if col not in self.df.columns]
            if invalid_columns:
                return {
                    "status": "error",
                    "message": f"Columns not found for datetime conversion: {', '.join(invalid_columns)}",
                }

            try:
                for col in dt_columns:
                    if datetime_format:
                        self.df[col] = pd.to_datetime(
                            self.df[col], format=datetime_format
                        )
                    else:
                        self.df[col] = pd.to_datetime(self.df[col])
                modifications.append(
                    f"Converted columns to datetime: {', '.join(dt_columns)}"
                )
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error converting to datetime: {str(e)}",
                }

        # Fill NA values if specified
        if fill_na and fill_value:
            na_columns = [col.strip() for col in fill_na.split(",")]
            invalid_columns = [col for col in na_columns if col not in self.df.columns]
            if invalid_columns:
                return {
                    "status": "error",
                    "message": f"Columns not found for NA filling: {', '.join(invalid_columns)}",
                }

            try:
                for col in na_columns:
                    if fill_value.lower() == "mean":
                        if pd.api.types.is_numeric_dtype(self.df[col]):
                            self.df[col] = self.df[col].fillna(self.df[col].mean())
                        else:
                            return {
                                "status": "error",
                                "message": f"Cannot use mean to fill non-numeric column: {col}",
                            }
                    elif fill_value.lower() == "median":
                        if pd.api.types.is_numeric_dtype(self.df[col]):
                            self.df[col] = self.df[col].fillna(self.df[col].median())
                        else:
                            return {
                                "status": "error",
                                "message": f"Cannot use median to fill non-numeric column: {col}",
                            }
                    elif fill_value.lower() == "mode":
                        # Mode returns a Series, so we get the first value
                        self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
                    else:
                        # Use the specified value
                        self.df[col] = self.df[col].fillna(fill_value)

                modifications.append(
                    f"Filled NA values in columns: {', '.join(na_columns)}"
                )
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error filling NA values: {str(e)}",
                }

        if not modifications:
            return {"status": "warning", "message": "No modifications were specified."}

        # Return success with summary of changes
        return {
            "status": "success",
            "message": "; ".join(modifications),
            "shape": list(self.df.shape),
        }

    def encode_categorical_columns(
        self,
        columns: Optional[str] = None,
        method: Optional[str] = None,
        drop_original: Optional[bool] = None,
        max_categories: Optional[int] = None,
    ) -> dict:
        """Encode categorical columns to numerical format for machine learning and visualization.

        Args:
            columns (str, optional): Comma-separated names of columns to encode. If None or empty string, all object/category columns will be encoded.
            method (str, optional): Encoding method to use - 'one-hot', 'label', or 'ordinal'. Default is 'one-hot' if None or empty string is provided.
            drop_original (bool, optional): Whether to drop the original categorical columns after encoding. Default is True if None or empty string is provided.
            max_categories (int, optional): Maximum number of categories to one-hot encode (to avoid creating too many columns). Default is 10 if None or empty string is provided.

        Returns:
            dict: {
                'status': 'success' or 'error',
                'message': description of encoding process,
                'encoded_columns': list of created column names,
                'shape': new shape of the dataset after encoding
            }
        """
        if self.df is None:
            return {"status": "error", "message": "No DataFrame loaded."}

        # Set default values if None or empty string
        if method is None or method == "":
            method = "one-hot"
        if drop_original is None or drop_original == "":
            drop_original = True
        if max_categories is None or max_categories == "":
            max_categories = 10

        # Treat empty string for columns as None
        if columns == "":
            columns = None

        # Determine which columns to encode
        if columns:
            columns_list = [col.strip() for col in columns.split(",") if col.strip()]
            # Verify columns exist
            missing_cols = [col for col in columns_list if col not in self.df.columns]
            if missing_cols:
                return {
                    "status": "error",
                    "message": f"Columns not found: {', '.join(missing_cols)}",
                }
        else:
            # Select all object and category dtype columns
            columns_list = self.df.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()

        if not columns_list:
            return {
                "status": "error",
                "message": "No categorical columns found to encode.",
            }

        encoded_columns = []
        method = method.lower()

        try:
            if method == "one-hot":
                for col in columns_list:
                    # Check the number of unique values
                    unique_values = self.df[col].nunique()
                    if pd.isna(self.df[col]).any():  # Account for NA values
                        unique_values += 1

                    if unique_values > max_categories:
                        return {
                            "status": "error",
                            "message": f"Column '{col}' has {unique_values} categories, which exceeds the maximum of {max_categories} for one-hot encoding. Use 'label' or 'ordinal' encoding instead, or increase max_categories.",
                        }

                    # Apply one-hot encoding
                    dummies = pd.get_dummies(
                        self.df[col], prefix=col, dummy_na=pd.isna(self.df[col]).any()
                    )
                    self.df = pd.concat([self.df, dummies], axis=1)
                    encoded_columns.extend(dummies.columns.tolist())

                # Drop original columns if requested
                if drop_original:
                    self.df = self.df.drop(columns=columns_list)

                return {
                    "status": "success",
                    "message": f"One-hot encoded {len(columns_list)} columns into {len(encoded_columns)} binary columns",
                    "encoded_columns": encoded_columns,
                    "original_columns": columns_list,
                    "shape": list(self.df.shape),
                }

            elif method == "label":
                from sklearn.preprocessing import LabelEncoder

                for col in columns_list:
                    # Create a new column name for the encoded version
                    new_col_name = f"{col}_encoded"

                    # Handle NaN values by creating a copy of the column
                    col_data = self.df[col].copy()
                    nan_mask = col_data.isna()

                    # Apply label encoding (0,1,2,...)
                    le = LabelEncoder()
                    col_data_filled = col_data.fillna(
                        "_NaN_"
                    )  # Temporary fill for encoding
                    self.df[new_col_name] = le.fit_transform(col_data_filled)

                    # Restore NaN values
                    self.df.loc[nan_mask, new_col_name] = np.nan

                    encoded_columns.append(new_col_name)

                # Drop original columns if requested
                if drop_original:
                    self.df = self.df.drop(columns=columns_list)

                return {
                    "status": "success",
                    "message": f"Label encoded {len(columns_list)} columns",
                    "encoded_columns": encoded_columns,
                    "original_columns": columns_list,
                    "shape": list(self.df.shape),
                }

            elif method == "ordinal":
                for col in columns_list:
                    # Create a new column name for the encoded version
                    new_col_name = f"{col}_ordinal"

                    # Get the sorted unique values (excluding NaN)
                    unique_vals = sorted([x for x in self.df[col].dropna().unique()])
                    # Create a mapping dictionary
                    val_map = {val: i for i, val in enumerate(unique_vals)}

                    # Apply the mapping
                    self.df[new_col_name] = self.df[col].map(val_map)
                    encoded_columns.append(new_col_name)

                # Drop original columns if requested
                if drop_original:
                    self.df = self.df.drop(columns=columns_list)

                return {
                    "status": "success",
                    "message": f"Ordinal encoded {len(columns_list)} columns",
                    "encoded_columns": encoded_columns,
                    "original_columns": columns_list,
                    "shape": list(self.df.shape),
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown encoding method '{method}'. Use 'one-hot', 'label', or 'ordinal'.",
                }

        except Exception as e:
            return {"status": "error", "message": f"Error during encoding: {str(e)}"}
