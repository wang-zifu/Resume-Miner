import os
import zipfile
# other tools useful in extracting the information from our document
import re
# to pretty print our xml:
import xml.dom.minidom

import glob, os
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
import string
import shutil

#os.environ['TIKA_SERVER_JAR'] = 'https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.23/tika-server-1.23.jar'
import tika
tika.initVM()
tika.TikaClientOnly = True
from tika import parser
from subprocess import Popen, PIPE

# import docx

# http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library
# from pdfminer3.layout import LAParams, LTTextBox
# from pdfminer3.pdfpage import PDFPage
# from pdfminer3.pdfinterp import PDFResourceManager
# from pdfminer3.pdfinterp import PDFPageInterpreter
# from pdfminer3.converter import PDFPageAggregator,TextConverter
# from io import StringIO
import sys, getopt
lemmatizer = WordNetLemmatizer()
exp_years = re.compile('((.*\d{1,2}[.]?[+]?[0-9]*[ ]*[\W]?[ ]*(?:years|year|months|month|yrs|yr).*)|((?:experience of)[ ]*[0-9][0-9]*[.]?[0-9]*[ ]*[\W]?}.*))')
linkedin_regex = r'^((http|https):\/\/)?+(www.linkedin.com\/)+[a-z]+(\/)+[a-zA-Z0-9-]{5,30}+$'
email_regex = r'[A-Za-z0-9+_.]+[@][A-Za-z.-_]+[.][a-z]+'
phone_regex = r'[+]?\d{1,2}?[-]?[ ]?\d{5}[ ]?[-]?\d{5,}'
work_duration_regex = r".*[-]?[ ]*\d{2,4}[ ]*\b(?:to|To|-| - )[ ]*[a-zA-Z0-9'-]*[ ]*[a-zA-Z0-9'-]*.*(?:\n).*"

'''
filenames=[]
resume_list = []
names = []
summary = []
work_experience = []
education = []
technical_skills = []
extra_curr = []
awards = []
file_list = []
required_headings = []
email_data = []
linkedin_data = []
phone_data=[]
years_experience_data = []
work_duration_data = []
total=0
'''
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('wordnet')

def sortSecond(val):
    return val[1]


def sortLength(val):
    return len(val)


def remove_number(text):
    pattern = '[0-9]'
    list = [re.sub(pattern, '', i) for i in text.split(" ")]
    return " ".join(list)

def replacesub(input, pattern, replaceWith): 
    return input.replace(pattern, replaceWith)


def convert_pdf_to_txt(path):


    resource_manager = PDFResourceManager()
    fake_file_handle = StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(path, 'rb') as fh:

        for page in PDFPage.get_pages(fh,
                                    caching=True,
                                    check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    return text
   
def document_to_text(file_path):
    if file_path.split('.')[-1].strip() == "doc":
        cmd = ['antiword', file_path]
        p = Popen(cmd, stdout=PIPE,shell=True)
        stdout, stderr = p.communicate()
        return stdout.decode('ascii', 'ignore')
    elif file_path.split('.')[-1].strip() == "docx":
        doc = docx.Document(file_path)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)    
    elif file_path.split('.')[-1].strip() == "odt":
        cmd = ['odt2txt', file_path]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode('ascii', 'ignore')
    elif file_path.split('.')[-1].strip() == "pdf":
        return convert_pdf_to_txt(file_path)


def get_details_from_path(path):
    names=[]
    resume_list=[]
    filenames=[]
    files=[]
    num=0
    path_resume=path
    for extension in ['*.docx', '*.doc', '*.pdf','*.odt']:
        for filename in glob.glob(os.path.join(path_resume, extension)):
            with open(filename, 'rb') as file:
                 binaryData = file.read()
                 files.append(binaryData)
            print('filename: ', filename)
            #text1 = document_to_text(filename)
            parsed = parser.from_file(filename)
            text = parsed["content"]  # To get the content of the file
            #text = str(text1)
            current = filename.lower().split("/")[-1].split(".")[0]
            filenames.append(filename)
            names.append(current)
            #print("Loading " + str(num) + " " + str(current))
            final_str = ''
            for char in text.__str__():
                if char in string.printable or char=='\n':
                    final_str += char
            resume_list.append(final_str)
            num = num + 1
    
    return resume_list,names,num,filenames,files

def get_title_desc():
    path = "titles"
    path_title = os.path.abspath(path)
    file_list=[]
    names = []
    summary = []
    work_experience = []
    education = []
    technical_skills = []
    extra_curr = []
    awards = []
    for filename in glob.glob(os.path.join(path_title, '*.txt')):
        f = open(filename, 'r')
        text = f.read()
        file_list.append(f)
        final_str = ''
        text = text.lower()
        # if os.path.splitext(filename)[0].split("\\")[-1] == 'summary':
        #     for tex in text.splitlines():
        #         summary.append(tex)
        # elif os.path.splitext(filename)[0].split("\\")[-1] == 'education':
        #     for tex in text.splitlines():
        #         education.append(tex)
        # elif os.path.splitext(filename)[0].split("\\")[-1] == 'technical_skills':
        #     for tex in text.splitlines():
        #         technical_skills.append(tex)
        # elif os.path.splitext(filename)[0].split("\\")[-1] == 'work_experience':
        #     for tex in text.splitlines():
        #         work_experience.append(tex)
        # elif os.path.splitext(filename)[0].split("\\")[-1] == 'extra_curr':
        #     for tex in text.splitlines():
        #         extra_curr.append(tex)
        # elif os.path.splitext(filename)[0].split("\\")[-1] == 'awards':
        #     for tex in text.splitlines():
        #         awards.append(tex)

        if str(filename).find('summary')>=0:
            for tex in text.splitlines():
                summary.append(tex)
        elif str(filename).find('education')>=0:
            for tex in text.splitlines():
                education.append(tex)
        elif str(filename).find('technical_skills')>=0:
            for tex in text.splitlines():
                technical_skills.append(tex)
        elif str(filename).find('work_experience')>=0:
            for tex in text.splitlines():
                work_experience.append(tex)
        elif str(filename).find('extra_curr')>=0:
            for tex in text.splitlines():
                extra_curr.append(tex)
        elif str(filename).find('awards')>=0:
            for tex in text.splitlines():
                awards.append(tex)
    return summary, technical_skills, work_experience, education, extra_curr, awards

def get_headings(resume_list, names):
    heading_list = [[None for _ in range(0)] for _ in range(100)]

    # line by line from left find words <=4
    line_num = 0

    # get headings
    for i in range(len(resume_list)):
        # print("\n\n")
        # print(names[i])
        line_num = 0
        k = 0
        for line in resume_list[i].lower().splitlines():
            k = 0
            if len(nltk.word_tokenize(line.strip())) <= 3:
                str1 = line.strip().replace("\t", " ")
                if str1:
                    k = 1
                    heading_list[i].append([line_num, str1])
                # print(line.strip())
            if line.strip().__contains__(":"):
                str1 = line.strip().replace("\t", " ")
                str1 = str1.split(":")[0]
                if str1 and k == 0:
                    heading_list[i].append((line_num, " ".join(str1.strip().split())))

            line_num = line_num + 1
        # print(heading_list[i])
    return heading_list

def get_parsed_resume(resume_list, names, which_resume):
    names = []
    summary = []
    work_experience = []
    education = []
    technical_skills = []
    extra_curr = []
    awards = []
    heading_list = [[None for _ in range(0)] for _ in range(100)]
    classify_headings = heading_list
    required_headings = []

    # get dataset names for each title
    summary, technical_skills, work_experience, education, extra_curr, awards = get_title_desc()

    # get headings of all
    heading_list = get_headings(resume_list, names)
    print("HEADING LIST: \n " + str(which_resume))
    print(heading_list[which_resume])
    print("\n")
    k = 0
    # tokenize, lemma both
    # and then check for
    # correct matching
    for num, head in heading_list[which_resume]:
        '''

        str = " ".join((head.split(":")[0]).split()).strip()
        k=0
        for st in work_experience:
            if st.find(str)>=0:
                classify_headings[2].append((str,num,2))
                k=1
        if k==1:
            continue
        
        for st in summary:
            if st.find(str)>=0:
                classify_headings[0].append((str,num,0))
                k=1
        if k==1:
            continue

        for st in technical_skills:
            if st.find(str)>=0:
                classify_headings[1].append((str,num,1))
                k=1
        if k==1:
            continue

        for st in education:
            if st.find(str)>=0:
                classify_headings[3].append((str,num,3))
                k=1
        if k==1:
            continue

        for st in extra_curr:
            if st.find(str)>=0:
                classify_headings[4].append((str,num,4))
                k=1
        if k==1:
            continue

        for st in awards:
            if st.find(str)>=0:
                classify_headings[5].append((str,num,5))
                k=1
        if k==1:
            continue


        '''
        str1 = " ".join((head.split(":")[0]).split())
        str2 = str1.strip()
        #str_lemma = [lemmatizer.lemmatize(word) for word in str2.split()]
        #str2 = " ".join(str_lemma)
        #str2 = str2.strip()
        flag=0

        for i in range(len(work_experience)):
            title_lemma = [lemmatizer.lemmatize(word) for word in work_experience[i].split()]
            title = " ".join(title_lemma)
            title = title.strip()
            flag = 0
            if str2.find(title)>=0:
                flag = 1
            if flag == 1:
                classify_headings[3].append((str2, num, 3))
                break
        if flag==1:
             continue

        for i in range(len(summary)):
            title_lemma = [lemmatizer.lemmatize(word) for word in summary[i].split()]
            title = " ".join(title_lemma)
            title = title.strip()
            flag = 0
            if str2.find(title)>=0:
                flag = 1
            if flag == 1:
                classify_headings[0].append((str2, num, 0))
                break
        if flag == 1:
            continue

        for i in range(len(education)):
            title_lemma = [lemmatizer.lemmatize(word) for word in education[i].split()]
            title = " ".join(title_lemma)
            title = title.strip()
            flag = 0
            if str2.find(title)>=0:
                flag = 1
            if flag == 1:
                classify_headings[1].append((str2, num, 1))
                break
        if flag == 1:
            continue

        for i in range(len(technical_skills)):
            title_lemma = [lemmatizer.lemmatize(word) for word in technical_skills[i].split()]
            title = " ".join(title_lemma)
            title = title.strip()
            flag = 0
            if str2.find(title)>=0:
                flag = 1
            if flag == 1:
                classify_headings[2].append((str2, num, 2))
                break
        if flag == 1:
            continue

        for i in range(len(extra_curr)):
            title_lemma = [lemmatizer.lemmatize(word) for word in extra_curr[i].split()]
            title = " ".join(title_lemma)
            title = title.strip()
            flag = 0
            if str2.find(title)>=0:
                flag = 1
            if flag == 1:
                classify_headings[4].append((str2, num, 4))
                break
        if flag == 1:
            continue

        for i in range(len(awards)):
            title_lemma = [lemmatizer.lemmatize(word) for word in awards[i].split()]
            title = " ".join(title_lemma)
            title = title.strip()
            flag = 0
            if str2.find(title)>=0:
                flag = 1
            if flag == 1:
                classify_headings[5].append((str2, num, 5))
                break
        if flag == 1:
            continue

    for i in range(6):
        for arr in classify_headings[i]:
            if arr != []:
                required_headings.append(arr)

    required_headings.append(('eof', np.Infinity, 6))
    required_headings.sort(key=sortSecond)

    print("REQD HEADINGS:  \n" + str(which_resume))
    print(required_headings)
    print("\n")

    each_summary = []
    each_tech_skills = []
    each_work_exp = []
    each_education = []
    each_extra = []
    each_awards=[]

    p = 0
    for i in range(len(required_headings) - 1):
        # print("outer loop", p)
        if required_headings[p] != [] and required_headings[p + 1] != []:
            line_val = 0
            strin = []
            for line in resume_list[which_resume].splitlines():
                if required_headings[p][1] <= line_val < required_headings[p + 1][1]:
                    strin.append(" ".join(line.strip().split()))
                line_val = line_val + 1
            str2 = "\n".join(strin)
            #print("str2 ",str2 + "\n\n")
            head_additional = " ".join(required_headings[p][0].strip().replace(":", "").split())
            if required_headings[p][2] == 0 or head_additional in summary:
                each_summary.append(str2)
            elif required_headings[p][2] == 1 or head_additional in education:
                each_education.append(str2)
            elif required_headings[p][2] == 2 or head_additional in technical_skills:
                each_tech_skills.append(str2)
            elif required_headings[p][2] == 3 or head_additional in work_experience:
                each_work_exp.append(str2)
            elif required_headings[p][2] == 4 or head_additional in extra_curr:
                each_extra.append(str2)
            elif required_headings[p][2] == 5 or head_additional in awards:
                each_awards.append(str2)

        p = p + 1

    return each_summary, each_tech_skills, each_work_exp, each_education, each_extra,each_awards

def get_experience(resume_list, names):
    exp_list_complete = []
    for i in range(len(resume_list)):
        # print("\n\n")
        # print(names[i])
        exp_list = exp_years.findall(resume_list[i])
        if exp_list:
            exp_list_complete.append(" ".join(set(exp_list[0][1:])))
        else:
            exp_list_complete.append("NA")
    return exp_list_complete


def get_email(resume_list, names):
    email = []
    data = []
    for i in range(len(resume_list)):
        data = re.findall(email_regex, str(resume_list[i]))
        if data:
            email.append(data)
        else:
            email.append(['NA'])
    return email


def get_phone(resume_list,names):
    phone = []
    data = []
    for i in range(len(resume_list)):
        data = re.findall(phone_regex, str(resume_list[i]))
        if data:
            phone.append(data)
        else:
            phone.append(['NA'])
    return phone

def get_work_duration(resume_list,names):
    duration = []
    data = []
    for i in range(len(resume_list)):
        data = re.findall(work_duration_regex, str("\n".join(resume_list[i].splitlines())))
        dur=[]
        for d in data:
            if re.search('[a-zA-Z]', str(d)):
                da = replacesub(str(d),'\n',' >> ')
                dur.append(da)
        if dur:
            duration.append(dur)
        else:
            duration.append(['NA'])
    return duration


def get_linkedin(resume_list, names):
    linkedin = []
    data = []
    for i in range(len(names)):
        word_list = resume_list[i].lower().split()
        data = []
        for word in word_list:
            if word.find("linkedin.com/in/") >= 0:
                data.append(word)
        if data == []:
            linkedin.append("NA")
        else:
            data.sort(key=sortLength, reverse=True)
            linkedin.append(data[0].lower())
    return linkedin

def get_primary_details(resume_list,names):

    email_data = []
    linkedin_data = []
    phone_data=[]
    years_experience_data = []
    work_duration_data = []
    # get experience based on years regex
    exp_list = get_experience(resume_list, names)
    for exp in exp_list:
        years_experience_data.append(exp.splitlines()[0])

    # get email of each
    email_list = get_email(resume_list, names)
    for email in email_list:
        if email:
            email_data.append(" ".join(set(email)))

    # get linkedin url of each
    linkedin_list = get_linkedin(resume_list, names)
    for url in linkedin_list:
        linkedin_data.append(url)

    #get phone number
    phone_list = get_phone(resume_list,names)
    for phone in phone_list:
        phone_data.append(phone)

    #get work duration
    duration_list = get_work_duration(resume_list,names)
    for dur in duration_list:
        work_duration_data.append(dur)

    return dict(zip(["email","linkedin","phone","exp_years","duration"],[email_data,linkedin_data,phone_data,years_experience_data,work_duration_data]))



def get_secondary_details(resume_list,names):
    # get parsed resume for given input
    summary_text = []
    tech_skill_text = []
    work_exp_text = []
    education_text = []
    extra_text = []
    awards_text=[]

    # get all summary,exp,skill,extra_curr,education etc
    for i in range(len(names)):
        each_summary, each_tech_skills, each_work_exp, each_education, each_extra,each_awards = get_parsed_resume(resume_list, names, i)
        summary_text.append(" ".join(each_summary))
        tech_skill_text.append("\n".join(each_tech_skills))
        work_exp_text.append("\n".join(each_work_exp))
        education_text.append("\n".join(each_education))
        extra_text.append("\n".join(each_extra))
        awards_text.append("\n".join(each_awards))
        print(each_work_exp)
        print("parsing done for ",names[i])
    
    return dict(zip(["summary","skills","experience","education","extra","awards"],[summary_text,tech_skill_text,work_exp_text,education_text,extra_text,awards_text]))    


def get_resume_details(path):
    resume_list,names,total,filenames,files = get_details_from_path(path)
    dict1 = get_primary_details(resume_list,names)
    dict2 = get_secondary_details(resume_list,names)
    return dict(zip(["dict1","dict2","total","filename","complete","files"],[dict1,dict2,total,filenames,resume_list,files]))

def change_permissions_recursive(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root,d) for d in dirs]:
            os.chmod(dir, mode)
    for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)

def get_numbers(text):
    return re.findall('\d*\.?\d+',text)

def check_any(cand,any_l):
    fdist = nltk.FreqDist()
    fdist = get_freq(str(cand.complete_resume).lower())
    if any_l==['']:
        return 1
    if any(word.lower() in fdist.keys() for word in any_l):
        return 1
    else:
        return 0

def check_all(cand,all_l):
    fdist = nltk.FreqDist()
    fdist = get_freq(str(cand.complete_resume).lower())
    if all_l==['']:
        return 1
    if all(word.lower() in fdist.keys() for word in all_l):
        return 1
    else:
        return 0

def get_freq(p):
    fdist = nltk.FreqDist()
    for sentence in nltk.tokenize.sent_tokenize(p):
        for word in nltk.tokenize.word_tokenize(sentence):
            fdist[word] +=1
    return fdist


def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)

