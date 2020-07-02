import re
from xml.etree import ElementTree as ET


# TEXTUAL EXTRACTION FUNCTIONS
###############################################################################################

# GET TEXTUAL DATA INTO STRING
def getTextFromTagNode(node):
    textString = re.sub(r"(&#.*?;)",'',(re.sub(r"(<.*?>)",'', ET.tostring(node).decode("utf-8"))))
    return textString
    # textString = re.sub(r"(..*?     .*?.)",'.',re.sub(r"(FIG\S|FIGs\S|FIGS\S)",'     ',re.sub(r"(\.\.|\.\,|\,\.)",'.',re.sub(r"(\(.\)|\(\)|\(|\)|VI|II)",'',(re.sub(r"(<.*?>|&#.*?;|[\n\r\t]|Field of the Invention|\d+)",'', ET.tostring(node).decode("utf-8")))))))
    # textString = re.sub(r"(\n)",' ',re.sub(r"(<.*?>|&#.*?;)",'', ET.tostring(node).decode("utf-8")))

# SPLIT TEXT ACCORDING TO PATTERN
def split(txt, seps):
    default_sep = 'separator_split'

    for sep in seps:
        txt = txt.replace(sep, default_sep)

    return [i.strip() for i in txt.split(default_sep)]

def clean_txt(part):
	return ' '.join(part.replace('Field of the Invention','').replace('Description of the Related Art','').replace('Discussion of the Prior Art','').replace('Description of the Prior Art','').replace('FIG.',' ').replace('FIG',' ').replace('U.','').replace('S.','').replace('Pat.','').replace('Nos.','').replace('No.','').replace('etc.)','').replace('etc. )','').replace('etc. ,','').replace('i. e.','').replace(".",". ").replace('e. g.','').replace('(','').replace(')','').split())

