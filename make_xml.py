import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import re

def safe_ascii(text):
	return re.sub(r'[\\/:"*?<>|]+', "", text)

def remove_empty_lines(text):
	return os.linesep.join([s for s in text.splitlines() if s.replace('\n','').replace('\r', '').strip()])

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)    
    return reparsed.toprettyxml(indent="\t")

def add_key(content_node, row, col, width, height, text):
	key = ET.SubElement(content_node,"DynamicKey")

	# Attributes
	key.set('Row', str(row))
	key.set('Col', str(col))
	key.set('Width', str(width))
	key.set('Height', str(height))

	# Elements
	label_elem = ET.SubElement(key, "Label")
	label_elem.text = text
	text_elem = ET.SubElement(key, "Text")
	text_elem.text = text

def save_file(xml_root, filename):
	text = prettify(xml_root)
	with open(filename, "w") as f:
		for line in text.splitlines():
			if (line.strip()):
				f.write(line)
				f.write("\n")

def setup_keyboard(hidden=True):
	# Load basic content
	tree = ET.parse('skeleton.xml')
	root = tree.getroot()

	# Top level elements
	rows_element = ET.fromstring("<Rows>" + str(total_rows) + "</Rows>")
	cols_element = ET.fromstring("<Cols>" + str(total_cols) + "</Cols>")
	hidden_element = ET.fromstring("<HideFromKeyboardMenu>" + str(hidden) + "</HideFromKeyboardMenu>")

	# insert at top
	grid = tree.find('Grid')
	grid.insert(0, rows_element)
	grid.insert(1, cols_element)

	# Content node contains all the keys
	content = tree.find('Content')

	return tree, content

def make_text_keyboard(all_chars):
	tree, content = setup_keyboard()


	# suggestions_element = ET.fromstring("<SuggestionRow Width=\"" + str(total_cols) +"\"/>")
	# scratchpad_element = ET.fromstring("<Scratchpad Width=\"" + str(total_cols) +"\"/>")		

	# content.insert(0, suggestions_element)
	# content.insert(1, scratchpad_element)

	# Add keys one by one, starting on third row (below scratchpad and suggestions)
	curr_row = 2 # use enumerate for less verbose indexing
	curr_col = 0
	for char in all_chars:		
		add_key(content, curr_row, curr_col, 1, 1, char)
		curr_col += 1
		if curr_col >= total_cols:
			curr_col = 0
			curr_row += 1

	save_file(tree.getroot(), safe_ascii("z__sub-" + all_chars+ ".xml"))

total_rows = 4
total_cols = 4 

# Content node contains all the keys
tree, content = setup_keyboard()

keys = ["abcdefgh", "ijklmnop", "qrstuvwx", "yz?!,;.",] #todo: split with newline for label
# TODO special char ␣ will need special consideration

# Add keys one by one

curr_row = 0
curr_col = 0
for key in keys:
	make_text_keyboard(key)
	add_key(content, curr_row, curr_col, 1, 1, key)
	curr_col += 1
	if curr_col >= total_cols:
		curr_col = 0
		curr_row += 1

#TODO: think about how we keep track of links vs text, text vs actions


save_file(tree.getroot(), "wibble.xml")
