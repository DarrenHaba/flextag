import flextag

# Example LLM response in FlexTag formatting
response = '''
<<-- WORD[0]:
try
-->>

<<-- MEANING[0]:
Begins a block to catch exceptions in Python.
-->>
'''

# Convert to records (list of dictionaries)
results = flextag.flex_to_records(response)

# Access first record
first_record = results[0]
print("Keyword:", first_record['WORD'])
print("Definition:", first_record['MEANING'])