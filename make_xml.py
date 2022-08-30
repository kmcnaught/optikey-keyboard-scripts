#!/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import re

from more_itertools import chunked
from more_itertools import flatten

def safe_ascii(text):
	return re.sub(r'[\\/\×÷ç:"\'*?<>|␣—]+', "", text)

def remove_empty_lines(text):
	return os.linesep.join([s for s in text.splitlines() if s.replace('\n','').replace('\r', '').strip()])

def prettify(elem):
	"""Return a pretty-printed XML string for the Element.
	"""
	rough_string = ET.tostring(elem, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="\t").replace("&amp;&amp;","&")

def add_deadbutton(content_node, row, col, width, height):
	key = ET.SubElement(content_node,"DynamicKey")

	# Attributes
	key.set('BackgroundColor', "#010101")
	key.set('Row', str(row))
	key.set('Col', str(col))
	key.set('Width', str(width))
	key.set('Height', str(height))

def add_textkey(content_node, row, col, width, height, text):
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
	if text == '␣':
		text_elem.text = '&&#32;'
	action_elem = ET.SubElement(key, "Action")
	action_elem.text = "BackFromKeyboard"

def add_linkkey(content_node, row, col, width, height, text, link):
	key = ET.SubElement(content_node,"DynamicKey")

	# Attributes
	key.set('Row', str(row))
	key.set('Col', str(col))
	key.set('Width', str(width))
	key.set('Height', str(height))

	# Elements
	label_elem = ET.SubElement(key, "Label")
	label_elem.text = split_label(text)
	link_elem = ET.SubElement(key, "ChangeKeyboard")
	link_elem.text = link
	link_elem.set('BackReturnsHere', "True")

def split_label(text):
	L = len(text)
	if (L > 4):
		split_length = (int)((L+1)/2)
		t1 = text[0:split_length]
		t2 = text[split_length:]
		text = t1 + "\n" + t2
	return text

def save_file(xml_root, filename):
	text = prettify(xml_root)
	with open(filename, "w") as f:
		for line in text.splitlines():
			if (line.strip()):
				f.write(line)
				f.write("\n")

def setup_keyboard(name=None,hidden=True):
	# Load basic content
	tree = ET.parse('skeleton.xml')
	root = tree.getroot()

	# Top level elements
	rows_element = ET.fromstring("<Rows>" + str(total_rows) + "</Rows>")
	cols_element = ET.fromstring("<Cols>" + str(total_cols) + "</Cols>")
	hidden_element = ET.fromstring("<HideFromKeyboardMenu>" + str(hidden) + "</HideFromKeyboardMenu>")

	root.insert(2, hidden_element)  # 2 means it being the third tag (in this moment)

	if name:
		name_element = ET.fromstring("<Name>" + str(name) + "</Name>")
		root.insert(0, name_element) # so hidden_element will be the forth tag

	# insert at top
	grid = tree.find('Grid')
	grid.insert(0, rows_element)
	grid.insert(1, cols_element)

	# Content node contains all the keys
	content = tree.find('Content')

	return tree, content

def make_text_keyboard(all_chars):
	tree, content = setup_keyboard()

	# See at the skeleton.xml the initial couple keyboard's lines:
	# SuggestionRow and Scratchpad related.
	#
	# So here we add keys one by one starting on third row...

	curr_row = 6 # starts after SuggestionRow and Scratchpad lines

	all_chars = list(chunked(all_chars, 4))
	for chunk in all_chars:
		curr_col = 5 # starts after button of no tracking at side
		add_deadbutton(content, curr_row, 0, 5, 5)
		for char in chunk:
			add_textkey(content, curr_row, curr_col, 5, 5, char)
			curr_col += 5 # each "typing" key is Width=5
		add_deadbutton(content, curr_row, curr_col, 5, 5)
		curr_row += 5 # each keyboard's line is Height=5

	all_chars = ''.join(list(flatten(all_chars)))
	fname = safe_ascii("z__sub-" + all_chars + ".xml")
	save_file(tree.getroot(), fname)
	return fname

total_rows = 20 # five keyboard's lines with four rows of grid each
total_cols = 30 #                 | SuggestionRow
                # 5 + 4 12  4 + 5 | scratchpad's line
                # 5 + 5+5+5+5 + 5 | typing line one
                # 5 + 5+5+5+5 + 5 | typing line two
                # 5 +  4[x5]  + 5 | utility line

# Content node contains all the keys
tree, content = setup_keyboard("SL 2.0", False)

keys = [
	"abcdefgh", "ijklmnop", "qrstuvwx", "yz?!,;.\"",
	"()-+×÷=~", "01234567", "89ç[\/']", "@$&%<>␣—"
]

# Add keys to top level one by one
curr_row = 6 # starts after SuggestionRow and Scratchpad lines

keys = list(chunked(keys, 4))
for chunk in keys:
	curr_col = 5 # starts after button of no tracking at side
	add_deadbutton(content, curr_row, 0, 5, 5)
	for key in chunk:
		link = make_text_keyboard(key)
		add_linkkey(content, curr_row, curr_col, 5, 5, key, link)
		curr_col += 5 # each "typing" key is Width=5
	add_deadbutton(content, curr_row, curr_col, 5, 5)
	curr_row += 5 # each keyboard's line is Height=5

# TODO: think about how we keep track of links vs text, text vs actions
save_file(tree.getroot(), "top.xml")
