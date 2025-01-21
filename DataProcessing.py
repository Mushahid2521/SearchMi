import os
import pandas as pd
from pandas import CategoricalDtype


class DataFile:
    """
    Store the file path, data, pre-processing steps
    """

    def __init__(self):
        self.input_data_path = ""
        self.input_dataframe = pd.DataFrame()
        self.output_labels = []
        self.input_abundance_dataframe = pd.DataFrame()
        self.input_metadata_dataframe = pd.DataFrame()
        self.feature_list_after_preprocessing = []
        self.preprocessed_abundance_dataframe = pd.DataFrame()

    def read_file(self, file_path):
        """
        Reads a CSV or Excel file (xls, xlsx) into self.input_dataframe.
        Returns the resulting DataFrame.
        """
        self.input_data_path = file_path

        if file_path.endswith('.csv'):
            try:
                self.input_dataframe = pd.read_csv(file_path, index_col=0)
            except Exception as e:
                print("Error loading the CSV file:", e)

        elif file_path.endswith(('.xlsx', '.xls')):
            try:
                self.input_dataframe = pd.read_excel(file_path, sheet_name=0, index_col=0)
            except Exception as e:
                print("Error loading the Excel file:", e)
        else:
            print("Error: Unrecognized file format.")

        return self.input_dataframe

    def set_preprocessed_abundance_dataframe(self, df):
        self.preprocessed_abundance_dataframe = df
        return self.preprocessed_abundance_dataframe

    def get_input_dataframe(self):
        """
        Returns the loaded input DataFrame, or None if empty.
        """
        if not self.input_dataframe.empty:
            return self.input_dataframe
        return None

    def get_abundance_input_dataframe(self):
        return self.input_abundance_dataframe

    def get_metadata_input_dataframe(self):
        return self.input_metadata_dataframe[self.output_labels]

    def set_output_labels(self, labels_list):
        """
        Splits self.input_dataframe into:
          - self.input_abundance_dataframe (all columns except labels_list)
          - self.input_metadata_dataframe (only columns in labels_list)
        """
        self.output_labels = labels_list

        # Make sure the input is not empty.
        if self.input_dataframe.empty:
            print("Warning: input_dataframe is empty.")
            return

        # Drop the output label columns from the abundance DataFrame
        # and keep only those labels for metadata.
        self.input_abundance_dataframe = self.input_dataframe.drop(columns=self.output_labels)
        self.input_metadata_dataframe = self.input_dataframe[self.output_labels]

    def check_consistency_of_input_data(self):
        """
        Checks whether the columns in the abundance DataFrame are all numeric.
        """
        if self.input_dataframe.empty or not self.output_labels:
            print("Warning: No data or no output labels set.")
            return False, "No data or no output labels set"

        # Drop the output labels from the original input DataFrame

        # Verify all columns are numeric
        all_numeric = all(pd.api.types.is_numeric_dtype(dtype) for dtype in self.input_abundance_dataframe.dtypes)
        if not all_numeric:
            print("All columns are not numeric, please ensure the abundance columns are numeric.")
            return False, "Rest of the abundance columns are not numerical!"

        for col in self.output_labels:
            # Use is_categorical_dtype to check if the column is categorical
            try:
                self.input_dataframe[col] = self.input_dataframe[col].astype('category')
            except Exception as e:
                print("Columns can not be converted to categorical values!")
                return False, "Columns can not be converted to categorical values!"

            if len(self.input_dataframe[col].unique()) != 2:
                return False, f"{col} doesn't have two groups!"

        return True, ""
