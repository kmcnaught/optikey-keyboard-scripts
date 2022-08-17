import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os

def remove_empty_lines(text):
	return os.linesep.join([s for s in text.splitlines() if s.strip()])

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)    
    return remove_empty_lines(reparsed.toprettyxml(indent="\t"))

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
	text = prettify(root)
	with open(filename, "w") as f:
		f.write(text)

def setup_keyboard():
	# Load basic content
	tree = ET.parse('skeleton.xml')
	root = tree.getroot()

	# Top level elements
	rows_element = ET.fromstring("<Rows>" + str(total_rows) + "</Rows>")
	cols_element = ET.fromstring("<Cols>" + str(total_cols) + "</Cols>")

	# insert at top
	grid = tree.find('Grid')
	grid.insert(0, rows_element)
	grid.insert(1, cols_element)

	# Content node contains all the keys
	content = tree.find('Content')

	return content

# def make_text_keyboard():


total_rows = 2
total_cols = 4 


# Content node contains all the keys
content = setup_keyboard()

keys = ["abcd\nefgh", "ijkl\nmnop", "qrst\nuvwx", "yz?!,;.",]
# TODO special char ␣ will need special consideration

# Add keys one by one

curr_row = 0
curr_col = 0
for key in keys:
	add_key(content, curr_row, curr_col, 1, 1, key)
	curr_col += 1
	if curr_col >= total_cols:
		curr_col = 0
		curr_row += 1

#TODO: think about how we keep track of links vs text, text vs actions


save_file(root, "wibble.xml")
