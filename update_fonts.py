#!/usr/bin/env python3
"""Replace all font-family references with Poppins"""

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all Arial font-family with Poppins
content = content.replace(
    "font-family: Arial, sans-serif",
    "font-family: 'Poppins', 'Segoe UI', sans-serif"
)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated all font-family declarations to Poppins!")
print("📊 Changes applied to app.py")
