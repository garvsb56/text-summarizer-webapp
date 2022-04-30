import streamlit as st
import trafilatura
import docx2txt
from summa.summarizer import summarize
from PIL import Image
from PyPDF2 import PdfFileReader
import pdfplumber
import pytesseract
#from bs4 import BeautifulSoup
import requests
import json
import re
headers = {"Authorization": "Bearer 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"}
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

def sum_out(input):
    output = query({
        "inputs": input ,
        "parameters": {"do_sample": False, "min_length": values[0],"max_length":values[1]},
    })
    return output[0]['summary_text']

def read_pdf(file):
    pdfReader = PdfFileReader(file)
    count = pdfReader.numPages
    all_page_text = ""
    for i in range(count):
        page = pdfReader.getPage(i)
        all_page_text += page.extractText()

    return all_page_text


def read_pdf_with_pdfplumber(file):
    with pdfplumber.open(file) as pdf:
        page = pdf.pages[0]
        return page.extract_text()


# import fitz  # this is pymupdf

# def read_pdf_with_fitz(file):
# 	with fitz.open(file) as doc:
# 		text = ""
# 		for page in doc:
# 			text += page.getText()
# 		return text

# Fxn
@st.cache
def load_image(image_file):
    img = Image.open(image_file)
    return img


st.title("Text Summarizer")
values = st.slider(
        'Select the length of summary',10, 200, (25, 75),step = 5)


def main():
    menu = ["Image", "DocumentFiles", "Text or URL"]
    choice = st.sidebar.selectbox("Menu", menu)
    text = ''
    if choice == "Image":
        st.subheader("Image")
        image_file = st.file_uploader("Upload Image", type=['png', 'jpeg', 'jpg'])
        # if st.button("Process"):
        if image_file is not None:
                # To See Details
                # st.write(type(image_file))
                # st.write(dir(image_file))
            file_details = {"Filename": image_file.name, "FileType": image_file.type, "FileSize": image_file.size}
            st.write(file_details)

            st.header("Text Image")
            img = load_image(image_file)
            st.image(img)

            # st.header("Extracted Text")
            text = pytesseract.image_to_string(img)
            # st.write(text)
            # st.header("Summarized Text")
            # st.write(sum_out(text))


    elif choice == "DocumentFiles":
        st.subheader("DocumentFiles")
        docx_file = st.file_uploader("Upload File", type=['txt', 'docx', 'pdf'])
        # if st.button("Process"):
        if docx_file is not None:
            file_details = {"Filename": docx_file.name, "FileType": docx_file.type, "FileSize": docx_file.size}
            st.write(file_details)
                # Check File Type
            if docx_file.type == "text/plain":
                    # raw_text = docx_file.read() # read as bytes
                    # st.write(raw_text)
                    # st.text(raw_text) # fails
                st.text(str(docx_file.read(), "utf-8"))  # empty
                text = str(docx_file.read(),"utf-8")  # works with st.text and st.write,used for futher processing
                    # st.text(raw_text) # Works
                    # st.write(raw_text)  # works
                    # st.header("Summarized Text")
                    # st.write(sum_out(raw_text))
            elif docx_file.type == "application/pdf":
                    # raw_text = read_pdf(docx_file)
                    # st.write(raw_text)
                try:
                    with pdfplumber.open(docx_file) as pdf:
                            # txt = ""
                        for i in range(len(pdf.pages)):
                            page = pdf.pages[i]
                            text += page.extract_text()
                            # st.header("Text from the Article")
                            # st.write(text)
                            # st.header("Summarized Text")
                            # st.write(sum_out(text))
                except:
                    st.write("None")


            elif docx_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    # Use the right file processor ( Docx,Docx2Text,etc)
                text = docx2txt.process(docx_file)  # Parse in the uploadFile Class directory
                    # st.write(raw_text)
                    # st.header("Summarized Text")
                    # st.write(sum_out(raw_text))

    else:
        st.subheader("Text or URL")
        text = st.text_area("Give the Text or URL Here")
        # if st.button("Process"):
        #     st.write("Input Text", text)
        #     st.header("Summarized Text")
        #     st.write(sum_out(txt))
        if st.button("Go to URL"):
            url = str(text)
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded,include_comments=False,include_tables=False,
                                           include_links=False,include_formatting=False,include_images=False,no_fallback=True)
            st.write(text)
            st.header("Summarized Text")
            part = text.split(' ')
            if len(part) >= 1024:
                part1 = (' ').join(part[:1024])
                sum1 = sum_out(summarize(part1, words=512))
            else:
                sum1 = sum_out(summarize(text, words=512))
            st.write(sum1)
            #st.write(text)
            # st.header("Text from the Article")
            #text = str(ARTICLE)
            #st.write(text)
            # st.header("Summarized Text")
            # st.write(sum_out(text))
    if st.button("Summary"):
        # st.header("Extracted Text")
        #text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", text)
        text = re.sub(r'https?://\S+', '', text)
        st.write(text)
        st.header("Summarized Text")

        part = text.split(' ')
        if len(part) >= 1024:
            part1 = (' ').join(part[:1024])
            sum1 = sum_out(summarize(part1, words=512))
        else:
            sum1 = sum_out(summarize(text, words=512))
        st.write(sum1)

if __name__ == '__main__':
    main()