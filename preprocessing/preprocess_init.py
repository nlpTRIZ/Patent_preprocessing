from xml.etree import ElementTree as ET
import re
import hashlib
import json


def hashhex(s):
    """Returns a heximal formated SHA1 hash of the input string."""
    h = hashlib.sha1()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


REMAP = {"-lrb-": "(", "-rrb-": ")", "-lcb-": "{", "-rcb-": "}",
         "-lsb-": "[", "-rsb-": "]", "``": '"', "''": '"'}


def clean(x):
    return re.sub(
        r"-lrb-|-rrb-|-lcb-|-rcb-|-lsb-|-rsb-|``|''",
        lambda m: REMAP.get(m.group()), x)


def load_json(p, lower):
	# extract text from json
    source = []
    tgt = []

    (a_lst,s_lst)=p
    
  
    source_s=''
    for sent in json.load(open(a_lst))['sentences']:
        tokens = [t['word'] for t in sent['tokens']]
        if (lower):
            tokens = [t.lower() for t in tokens]
        # print("toookkens",tokens)
        source.append(tokens)
        # source_s = [source_s + t for t in tokens][0]
        # print("source sr",source_s)
       

    for sent in json.load(open(s_lst))['sentences']:
        tokens = [t['word'] for t in sent['tokens']]
        if (lower):
            tokens = [t.lower() for t in tokens]

        tgt.append(tokens)

   
    source = [clean(' '.join(sent)).split() for sent in source]
    tgt = [clean(' '.join(sent)).split() for sent in tgt]

    return source, tgt



def format_to_lines_(params):
    f = params
    source, tgt = load_json(f, True)
    return {'src': source, 'tgt': tgt}


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
