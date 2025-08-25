# convert_encoding.py

# Try to read the file with UTF-16 encoding (which is likely the current encoding)
try:
    with open('datadump.json', 'r', encoding='utf-16') as f:
        content = f.read()
    print("File successfully read as UTF-16. Converting to UTF-8...")
    
    # Write the content back out as UTF-8
    with open('datadump_fixed.json', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully created 'datadump_fixed.json' with UTF-8 encoding!")
    
except UnicodeError:
    # If UTF-16 fails, try other common encodings
    try:
        with open('datadump.json', 'r', encoding='utf-8') as f:
            content = f.read()
        print("File is already UTF-8. No conversion needed.")
    except UnicodeError as e:
        print(f"Failed to read file with common encodings: {e}")