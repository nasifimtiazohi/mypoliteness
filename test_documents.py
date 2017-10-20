import os
import xml.etree.ElementTree as etree
import subprocess
import openpyxl
import shlex
import time
from openpyxl.utils import coordinate_from_string, column_index_from_string
import nltk.data
sd=nltk.data.load('tokenizers/punkt/english.pickle')

"""
Some sample request documents, pre-processed 
and ready for politeness classification.

Shows expected format of documents--
Each document is a dict with fields
'text', 'sentences', and 'parses'

the 'score' field is only required
when training models. 
A score > 0.0 means the request is polite.

"""
TEST_DOCUMENTS=[]
#TEST_DOCUMENTS = [
#    # Polite requests
#    # Req 1
#    {
#        "text": "Have you found the answer for your question? If yes would you please share it?", 
#        "sentences": [
#            "Have you found the answer for your question?", 
#            "If yes would you please share it?"
#        ],
#        "parses": [
#            ["csubj(found-3, Have-1)", "dobj(Have-1, you-2)", "root(ROOT-0, found-3)", "det(answer-5, the-4)", "dobj(found-3, answer-5)", "poss(question-8, your-7)", "prep_for(found-3, question-8)"], 
#            ["prep_if(would-3, yes-2)", "root(ROOT-0, would-3)", "nsubj(would-3, you-4)", "ccomp(would-3, please-5)", "nsubj(it-7, share-6)", "xcomp(please-5, it-7)"]
#        ],
#        "score": 0.7
#    }, 
#    # Req 2
#    {
#        "text": "Sorry :) I dont want to hack the system!! :) is there another way?", 
#        "sentences": [
#            "Sorry :) I dont want to hack the system!!", 
#            ":) is there another way?"
#        ],
#        "parses": [
#            ["nsubj(dont-5, I-4)", "xsubj(hack-8, I-4)", "rcmod(-RRB--3, dont-5)", "dep(dont-5, want-6)", "aux(hack-8, to-7)", "xcomp(want-6, hack-8)", "det(!!-11, the-9)", "nn(!!-11, system-10)", "dobj(hack-8, !!-11)"], 
#            ["cop(there-4, is-3)", "root(ROOT-0, there-4)", "det(way-6, another-5)", "dep(there-4, way-6)"]
#        ],
#        "score": 0.8
#    },
#    # Impolite requests
#    # Req 3
#    {
#        "text": "What are you trying to do?  Why can't you just store the \"Range\"?",
#        "sentences": [
#            "What are you trying to do?",
#            "Why can't you just store the 'Range'?"
#        ],
#        "parses": [
#            ["dep(trying-4, What-1)", "aux(trying-4, are-2)", "nsubj(trying-4, you-3)", "xsubj(do-6, you-3)", "root(ROOT-0, trying-4)", "aux(do-6, to-5)", "xcomp(trying-4, do-6)"],
#            ["advmod(ca-2, Why-1)", "advcl(store-6, ca-2)", "neg(ca-2, n't-3)", "nsubj(store-6, you-4)", "advmod(store-6, just-5)", "root(ROOT-0, store-6)", "det(Range-9, the-7)", "dobj(store-6, Range-9)"]
#        ],
#        "score": -0.7
#    },
#    # Req 4
#    {
#        "text": "This was supposed to have been moved to &lt;url&gt; per the cfd. why wasn't it moved?",
#        "sentences": [
#            "this was supposed to have been moved to &lt;url&gt; per the cfd.",
#            "why wasn't it moved?"
#        ],
#        "parses": [
#            ["nsubjpass(supposed-3, this-1)", "xsubj(moved-7, this-1)", "auxpass(supposed-3, was-2)", "root(ROOT-0, supposed-3)", "aux(moved-7, to-4)", "aux(moved-7, have-5)", "auxpass(moved-7, been-6)", "xcomp(supposed-3, moved-7)", "prep_to(moved-7, url-10)", "det(cfd-14, the-13)", "prep_per(url-10, cfd-14)"],
#            ["advmod(n't-3, why-1)", "cop(n't-3, was-2)", "root(ROOT-0, n't-3)", "nsubj(moved-5, it-4)", "dep(n't-3, moved-5)"]
#        ],
#        "score": -0.9
#    }
#]
#determining type of TEST_DOCUMENTS
#print(type(TEST_DOCUMENTS))
# t=TEST_DOCUMENTS[0]
# print(type(t))
# p=t['parses']
# print(type(p))
# s=p[0]
# print(type(s))
# f=s[0]
# print(f)
# print(type(f))

#parsing xml file
global_parse_list=[]
def parse_xml_file_collapsed_dependancy(filename):
    tree=etree.parse(filename)
    root=tree.getroot()
    doc=root.getchildren()
    doc=doc[0]
    sentences=doc.getchildren()
    sentences=sentences[0]
    #print(sentences.tag, sentences.attrib)
    parselist=[]
    for sent in sentences.getchildren():
        #print(sent.tag,sent.attrib)
        sentlist=[]
        sentchildren= sent.getchildren()
        collapsed_dependancy=sentchildren[3]
        #print(collapsed_dependancy.tag)
        for c in collapsed_dependancy.getchildren():
            tStr=""
            d=c.attrib
            #print(d['type'])
            tStr+=d['type']
            tStr+='('
            for i,final_child in enumerate(c.getchildren()):
                word = final_child.text
                temp = final_child.attrib
                count = temp['idx']
                if i!=len(c.getchildren())-1:
                    tStr+= (word+'-'+count+", ")
                else:
                    tStr+= (word+'-'+count)
            tStr+=')'
            sentlist.append(tStr)
            #print(tStr)
        parselist.append(sentlist)
    return parselist
path="/home/nasif/tools/stanford-corenlp-2012-07-09/"
os.chdir(path)
print(os.getcwd())
wb=openpyxl.load_workbook('common.xlsx')
ws=wb.get_active_sheet()
for rows in ws['A2':'A114']:
    for cells in rows:
        val=cells.value
        xy=coordinate_from_string(cells.coordinate)
        col=column_index_from_string(xy[0])
        row=xy[1]
        #data pre-processing
        #val=os.linesp.join([s for s in val.splitlines() if s])
        val=val.replace('\n',' ').replace('\r',' ')
        f=open('input.txt','w+')
        f.write(val)
        f.seek(0)
        data=f.read()
        print("baler data is"+data)
        f.seek(0)
        f.close()
        java_com='java -cp "*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -file input.txt'
        args=shlex.split(java_com)
        output=subprocess.check_output(args)#this command generate a file named "input.txt.xml"
        #parse_xml_file_collapsed_dependancy('testInput.txt.xml')
        buff_dict={}
        buff_dict.update({'text':val})
        l=sd.tokenize(val.strip())
        buff_dict.update({'sentences':l})
        pl=parse_xml_file_collapsed_dependancy('input.txt.xml')
        if pl==[]:
        	print("amar bal")
        buff_dict.update({'parses':pl})
        TEST_DOCUMENTS.append(buff_dict)
print(TEST_DOCUMENTS)
        
import cPickle

f=open('dump.p','w')
cPickle.dump(TEST_DOCUMENTS,f,-1)
f.close







