# Read the input file
with open('federalist.txt', 'r') as file:
    content = file.read()

# Add comma after every closing curly brace
modified_content = content.replace('}', '},')

# Optional: remove extra commas if they occur before closing brackets like "]" or at the end of lines unnecessarily
import re
modified_content = re.sub(r'},(\s*[\]\}])', r'}\1', modified_content)  # Clean up , before ] or }
modified_content = re.sub(r'},(\s*$)', r'}\1', modified_content)       # Clean up trailing , on lines

# Write the modified content to a new file
with open('output.txt', 'w') as file:
    file.write(modified_content)
