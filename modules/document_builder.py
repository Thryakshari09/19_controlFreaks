import pandas as pd

# Load the dataset
df = pd.read_excel("data/World_Cricketers.xlsx")

documents = []

for _, row in df.iterrows():

    document = f"""
Name: {row['Name']}
Country: {row['Country']}
Role: {row['Role']}
Batting/Bowling Style: {row['Batting/Bowling Style']}
Era: {row['Era']}
Notable Achievements: {row['Notable Achievements']}
Background: {row['Background']}
"""

    documents.append(document.strip())

print(f"✅ Total Documents Created: {len(documents)}")

print("\n========== FIRST DOCUMENT ==========\n")
print(documents[0])