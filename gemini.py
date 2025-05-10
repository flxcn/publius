# pip install -q -U google-generativeai

from google import genai
from google.genai import types
from google.genai.errors import ClientError
from datetime import date
import re
import json
from dotenv import load_dotenv
import os
import itertools
import glob
from textwrap import dedent
import csv

backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

system_prompt = dedent("""\
Examine both documents carefully. Then, rate their overall similarity on a scale from -10 (completely dissimilar) to 10 (identical), with 0 representing neutrality. Please include a brief explanation highlighting the key factors that influenced your score."""
)

client = genai.Client(api_key=GEMINI_API_KEY)

# Get a list of all .txt files in the folder
file_paths = glob.glob("corpus/gemini_translations/*.txt")
print("Found documents:", file_paths)

# Read the text content from each document and store it in a dictionary
documents = {}
for file_path in file_paths:
    with open(file_path, "r", encoding="utf-8") as f:
        documents[file_path] = f.read()

# Prepare a results dictionary to store responses.
# We'll use document paths as keys for both rows and columns.
results = {}
doc_keys = list(documents.keys())
for doc in doc_keys:
    results[doc] = {}

def write_csv(results, doc_keys, filename="pairwise_comparisons.csv"):
    """Write the current results matrix to a CSV file."""
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        header = [""] + doc_keys
        writer.writerow(header)
        for doc in doc_keys:
            row = [doc]
            for col in doc_keys:
                if doc == col:
                    row.append("N/A")
                else:
                    row.append(results.get(doc, {}).get(col, ""))
            writer.writerow(row)

# Process every unique pair of documents
for doc1, doc2 in itertools.combinations(doc_keys, 2):
    text1 = documents[doc1]
    text2 = documents[doc2]
    print("Processing pair:")
    print("Document 1:", doc1)
    print("Document 2:", doc2)
    
    user_prompt = dedent(f"<DOCUMENT1>{text1}</DOCUMENT1>\n")
    user_prompt += dedent(f"<DOCUMENT2>{text2}</DOCUMENT2>\n")

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            ),
            contents=[user_prompt]
        )
        result_text = response.text.strip()
        print("Response:", result_text)
    except ClientError as ce:
        error_msg = str(ce)
        if "exceeds the maximum number of tokens" in error_msg:
            error_msg = "Error: input token count exceeds maximum allowed tokens."
        result_text = error_msg
        print("ClientError:", result_text)
    except Exception as e:
        result_text = f"Error: {e}"
        print(result_text)
    
    # Update the symmetric results matrix
    results[doc1][doc2] = result_text
    results[doc2][doc1] = result_text

    # Write the updated results to the CSV file after each pair is processed.
    write_csv(results, doc_keys)
