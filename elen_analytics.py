
''' 
This project focuses on developing proficiency in Git for version control, managing Python virtual environments, and handling various types of data. The project entails retrieving data from the web, processing it with suitable Python collections, and saving the processed data to files. 
 '''
# Standard library imports
import csv
import pathlib
import os
import json
import re
from collections import Counter

# External library imports (requires virtual environment)
import requests
import pandas as pd
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib is not installed. Please install it using 'pip install matplotlib'.")
    exit()
# Local module imports
import elen_project_setup



###############################
# Declare global variables
###############################

#Base data path (reused across functions)
base_data_path = pathlib.Path.cwd().joinpath('data')

def create_folder(folder_type, dataset_name):
    folder_path = base_data_path.joinpath(folder_type, dataset_name)
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path

##############################
# TXT
##############################

# Write data to a text file
def write_txt_file(folder_path, filename, data):
    file_path = folder_path / filename
    with file_path.open('w', encoding='utf-8') as file:
        file.write(data)
        print(f"Text data saved to {file_path}")

# Fetch data from a text file
def fetch_and_write_txt_data(folder_path, filename, url):
    response = requests.get(url)
     # Set the encoding explicitly to 'utf-8'
    response.encoding = 'utf-8'  # You can adjust this if the content requires a different encoding
    if response.status_code == 200:
        write_txt_file(folder_path, filename, response.text)
        return response.text
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

# Process and analyze text data
def process_txt_file(dataset_name, filename, url):
    folder_path = create_folder('txt', dataset_name)
    
    text_data = fetch_and_write_txt_data(folder_path, filename, url)
    
    if text_data:

        # Replace hyphens and slashes with spaces to prevent word combinations
        text_data = text_data.replace('-', ' ').replace('/', ' ')

        # Remove non-alphabetic characters and make lowercase
        clean_text = re.sub(r'[^A-Za-z\s]', '', text_data).lower()

        # Normalize multiple spaces and other whitespace characters
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        # Split the text into words
        words = clean_text.split()

        # Get word count and unique words using set
        word_count = len(words)
        unique_words = set(words)

        # Get frequency of each word
        word_freq = Counter(words)

        # Sort words by frequency
        sorted_word_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Count the total number of alphabetic characters (letters)
        letter_count = sum(1 for char in text_data if char.isalpha())

        # Prepare the analysis results
        analysis = (
            f"Total Word Count: {word_count}\n"
            f"Unique Words Count: {len(unique_words)}\n"
            f"Total Letter Count: {letter_count}\n\n"
            "Top 10 Most Frequent Words:\n"
        )

        # Append top 10 words by frequency
        for word, freq in sorted_word_freq[:10]:
            analysis += f"{word}: {freq}\n"

        # Save the analysis to a file
        write_txt_file(folder_path, f"analysis_{filename}", analysis)

# Example usage for TXT
#process_txt_file('data-txt', 'data-txt.txt', 'https://www.gutenberg.org/cache/epub/1513/pg1513.txt')



##############################
# Excel
##############################

def write_excel_file(folder_path, filename, data):
    file_path = folder_path.joinpath(filename)
    try:
        folder_path = pathlib.Path(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as file:
            file.write(data)
            print(f"Excel data saved to {file_path}")
    except IOError as e:
        print(f"IOError occurred while writing file: {e}")
    except OSError as e:
        print(f"OSError occurred while creating directories: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing file: {e}")
    finally:
        print("Write operation attempted.")
    return file_path  # Return the file path for further analysis

def fetch_and_write_excel_file(folder_path, filename, url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        file_path = write_excel_file(folder_path, filename, response.content)
        return file_path
    except requests.RequestException as e:
        print(f"RequestException occurred while fetching data: {e}")
    except ValueError as e:
        print(f"ValueError occurred while processing response content: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching data: {e}")
    finally:
        print("Fetch operation attempted.")
    return None

def save_analysis_results_to_txt(folder_path, filename, analysis):
    folder_path = pathlib.Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path.joinpath(filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(analysis)
        print(f"Analysis results saved to {file_path}")

def process_excel_file(dataset_name, filename, url):
    folder_path = create_folder('excel', dataset_name)
    # Fetch and write the Excel file
    file_path = fetch_and_write_excel_file(folder_path, filename, url)
    
    if file_path:
        try:
            # Determine the file extension and use the appropriate engine
            file_extension = pathlib.Path(file_path).suffix
            if file_extension == '.xlsx':
                engine = 'openpyxl'
            elif file_extension == '.xls':
                engine = 'xlrd'
            else:
                raise ValueError(f"Unsupported file extension: {file_extension}")
            
            # Load the Excel file into a pandas DataFrame
            df = pd.read_excel(file_path, engine=engine)
            
            # Inspect column names to identify valid columns
            print("\nColumn Names:\n")
            print(df.columns)

            # Create a folder specifically for analysis results
            analysis_folder_path = create_folder('excel', dataset_name)

            # Create a text analysis report
            analysis = "\nData Preview:\n"
            analysis += df.head().to_string()  # Convert data preview to string
            
            analysis += "\n\nSummary Statistics:\n"
            analysis += df.describe().to_string()  # Convert summary stats to string

            # Check Missing Data
            analysis += "\n\nMissing Data:\n"
            analysis += df.isnull().sum().to_string()

            # Save the text report
            save_analysis_results_to_txt(analysis_folder_path, 'excel_analysis.txt', analysis)

             # Example: Plotting a histogram
            if 'c1' in df.columns:  # Ensure 'c1' column exists
                ax = df['c1'].hist()  # Replace 'c1' with the appropriate column
                plt.title('Histogram of c1')  # Add a title
                plt.xlabel('c1')  # Label x-axis
                plt.ylabel('Frequency')  # Label y-axis
                plt.savefig(analysis_folder_path / 'histogram.png')  # Save plot as an image
                plt.close()  # Close the plot to avoid display issues
            else:
                print("Column 'c1' does not exist in the DataFrame.")
        
        except Exception as e:
            print(f"An error occurred while analyzing the Excel data: {e}")
        finally:
            print("Analysis operation attempted.")

# Example usage
#process_excel_file('data-excel', 'data-excel.xls', 'https://github.com/bharathirajatut/sample-excel-dataset/raw/master/cattle.xls')

###########################
# CSV
###########################

def write_csv_file(folder_path, filename, data):
    file_path = folder_path.joinpath(filename)
    try:
        folder_path = pathlib.Path(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as file:
            file.write(data)
            print(f"CSV data saved to {file_path}")
    except IOError as e:
        print(f"IOError occurred while writing file: {e}")
    except OSError as e:
        print(f"OSError occurred while creating directories: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing file: {e}")
    finally:
        print("Write operation attempted.")
    return file_path  # Return the file path for further analysis

def fetch_and_write_csv_file(folder_path, filename, url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        file_path = write_csv_file(folder_path, filename, response.content)
        return file_path
    except requests.RequestException as e:
        print(f"RequestException occurred while fetching data: {e}")
    except ValueError as e:
        print(f"ValueError occurred while processing response content: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching data: {e}")
    finally:
        print("Fetch operation attempted.")
    return None

def save_analysis_results_to_txt(folder_path, filename, analysis):
    folder_path = pathlib.Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path.joinpath(filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(analysis)
        print(f"Analysis results saved to {file_path}")

def process_csv_file(dataset_name, filename, url):
    folder_path = create_folder('csv', dataset_name)
    # Fetch and write the CSV file
    file_path = fetch_and_write_csv_file(folder_path, filename, url)
    
    if file_path:
        try:
            # Load the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)
            
            # Inspect column names to identify valid columns
            print("\nColumn Names:\n")
            print(df.columns)
            
            # Create a text analysis report
            analysis = "\nData Preview:\n"
            analysis += df.head().to_string()  # Convert data preview to string
            
            analysis += "\n\nSummary Statistics:\n"
            analysis += df.describe().to_string()  # Convert summary stats to string

            # Check for missing data
            analysis += "\n\nMissing Data:\n"
            analysis += df.isnull().sum().to_string()

            # Create a folder specifically for analysis results
            analysis_folder_path = create_folder('csv', dataset_name)

            # Save the text report in the analysis folder
            save_analysis_results_to_txt(analysis_folder_path, 'csv_analysis.txt', analysis)

           # Example: Plotting a histogram for the first numeric column found
            numeric_columns = df.select_dtypes(include=['number']).columns
            if 'c1' in df.columns:
                df['c1'].hist()  # If 'c1' exists, use it
                plt.savefig(analysis_folder_path.joinpath('histogram.png'))
                plt.show()
            elif len(numeric_columns) > 0:
                # If 'c1' doesn't exist, but there are other numeric columns, use the first one
                df[numeric_columns[0]].hist()
                plt.savefig(analysis_folder_path.joinpath('histogram.png'))
                plt.show()
            else:
                print("No numeric columns available for plotting.")
        
        except Exception as e:
            print(f"An error occurred while analyzing the CSV data: {e}")
        finally:
            print("Analysis operation attempted.")

# Example usage
#process_csv_file('data-csv', 'data-csv.csv','https://raw.githubusercontent.com/MainakRepositor/Datasets/master/World%20Happiness%20Data/2020.csv')

################
# JSON
###############

def write_json_file(folder_path, filename, data):
    file_path = folder_path.joinpath(filename)
    try:
        with file_path.open('w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"JSON data saved to {file_path}")
    except IOError as e:
        print(f"IOError occurred while writing file: {e}")
    except OSError as e:
        print(f"OSError occurred while creating directories: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing file: {e}")
    finally:
        print("Write operation attempted.")
    return file_path  # Return the file path for further analysis

def fetch_and_write_json_data(folder_path, filename, url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        json_data = response.json()  # Parse the JSON response content
        file_path = write_json_file(folder_path, filename, json_data)
        return file_path
    except requests.RequestException as e:
        print(f"RequestException occurred while fetching data: {e}")
    except ValueError as e:
        print(f"ValueError occurred while processing response content: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching data: {e}")
    finally:
        print("Fetch operation attempted.")
    return None

def save_simplified_data_to_file(folder_path, filename, data):
    folder_path = pathlib.Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path.joinpath(filename)
    try:
        with file_path.open('w', encoding='utf-8') as file:
            file.write("\n".join(data))
            print(f"Simplified data saved to {file_path}")
    except IOError as e:
        print(f"IOError occurred while writing file: {e}")
    except OSError as e:
        print(f"OSError occurred while creating directories: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing file: {e}")
    finally:
        print("Save operation attempted.")

def process_json_file(dataset_name, filename, url):
    folder_path = create_folder('json', dataset_name)
    # Fetch and write the JSON file
    file_path = fetch_and_write_json_data(folder_path, filename, url)
    
    if file_path:
        try:
            # Load the JSON file into a Python dictionary
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            simplified_data = []

            # Example: Extracting information about astronauts in space
            if "people" in json_data:
                simplified_data.append("Astronauts currently in space:\n")
                for person in json_data["people"]:
                    name = person.get("name")
                    craft = person.get("craft")
                    simplified_data.append(f"- {name} aboard {craft}")

            # Example: Count the number of astronauts
            num_astronauts = len(json_data.get("people", []))
            simplified_data.append(f"\nTotal number of astronauts in space: {num_astronauts}")

            # Save the simplified output to a text file
            save_simplified_data_to_file(folder_path, 'simplified_data.txt', simplified_data)
        
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {file_path}")
        except Exception as e:
            print(f"An error occurred while processing the JSON data: {e}")
        finally:
            print("Analysis operation attempted.")

# Example usage
#process_json_file('data-json', 'data.json', 'http://api.open-notify.org/astros.json')


##############################
# Main function
##############################

def main():
     '''Main function to demonstrate module capabilities.''' 

    # URLs for data
datasets = {
        "romeo_and_juliet_txt": ('txt', 'https://www.gutenberg.org/cache/epub/1513/pg1513.txt'),
        "happiness_csv": ('csv', 'https://raw.githubusercontent.com/MainakRepositor/Datasets/master/World%20Happiness%20Data/2020.csv'),
        "excel_data": ('excel', 'https://github.com/bharathirajatut/sample-excel-dataset/raw/master/cattle.xls'),
        "json_data": ('json', 'http://api.open-notify.org/astros.json'),
        "princess_bride_txt": ('txt', 'https://www.evenmere.org/~bts/Random-Collected-Documents/princess_bride.html'),
        "covid_csv":  ('csv', 'https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv')
    }
    # Folder names and filenames for data
romeo_and_juliet_txt_folder_path = 'romeo_and_juliet_data-txt'
happiness_csv_folder_path = 'happiness_data-csv'
excel_folder_path = 'data-excel'
json_folder_path = 'data-json'
princess_bride_folder_path = 'princess_bride-txt'
covid_folder_path = 'covid-csv'

romeo_and_juliet_txt_filename = 'romeo_and_juliet_data.txt'
happiness_csv_filename = 'happiness_data.csv'
excel_filename = 'data.xls'
json_filename = 'data.json'
princess_bride_filename = 'princess_bride.txt'
covid_filename = 'covid.csv'

# Process datasets based on type
for dataset_name, (file_type, url) in datasets.items():
        if file_type == 'txt':
            process_txt_file(dataset_name, f"{dataset_name}.txt", url)
        elif file_type == 'csv':
            process_csv_file(dataset_name, f"{dataset_name}.csv", url)
        elif file_type == 'excel':
            process_excel_file(dataset_name, f"{dataset_name}.xls", url)
        elif file_type == 'json':
            process_json_file(dataset_name, f"{dataset_name}.json", url)

if __name__ == "__main__":
    main()

#####################################
# Conditional Execution
#####################################

if __name__ == '__main__':
    main()
