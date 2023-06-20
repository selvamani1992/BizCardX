import streamlit as st
import easyocr
import cv2
import numpy as np
import pandas as pd
import re
from streamlit_option_menu import option_menu
import psycopg2
from PIL import Image
import io


selva = psycopg2.connect(host="localhost", user="postgres", password="Selva@123", port=5432, database="ocr")
guvi = selva.cursor()
reader = easyocr.Reader(['en'], gpu = False)

st.set_page_config(page_title="Bizcard", page_icon="",layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .sidebar .sidebar-content {
        width: 300px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("Bizcard")

def data_extrac(extract):
    for i in range(len(extract)):
        extract[i] = extract[i].rstrip(' ')
        extract[i] = extract[i].rstrip(',')
    result = ' '.join(extract)

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    website_pattern = r'[www|WWW|wwW]+[\.|\s]+[a-zA-Z0-9]+[\.|\][a-zA-Z]+'
    phone_pattern = r'(?:\+)?\d{3}-\d{3}-\d{4}'
    phone_pattern2 = r"(?:\+91[-\s])?(?:\d{4,5}[-\s])?\d{3}[-\s]?\d{4}"
    name_pattern = r'[A-Za-z]+\b'
    designation_pattern = r'\b[A-Za-z\s]+\b'
    address_pattern = r'\d+\s[A-Za-z\s,]+'
    pincode_pattern = r'\b\d{6}\b'

    name = designation = company = email = website = primary = secondary = address = pincode = None

    try:
        email = re.findall(email_pattern, result)[0]
        result = result.replace(email, '')
        email = email.lower()
    except IndexError:
        email = None
    try:
        website = re.findall(website_pattern, result)[0]
        result = result.replace(website, '')
        website = re.sub('[WWW|www|wwW]+ ', 'www.', website)
        website = website.lower()
    except IndexError:
        webstie = None
    phone = re.findall(phone_pattern, result)
    if len(phone) == 0:
        phone = re.findall(phone_pattern2, result)
    primary = None
    secondary = None
    if len(phone) > 1:
        primary = phone[0]
        secondary = phone[1]
        for i in range(len(phone)):
            result = result.replace(phone[i], '')
    elif len(phone) == 1:
        primary = phone[0]
        result = result.replace(phone[0], '')

    try:
        pincode = int(re.findall(pincode_pattern, result)[0])
        result = result.replace(str(pincode), '')
    except:
        pincode = 0
    # name = re.findall(name_pattern, result)[0]
    name = extract[0]
    result = result.replace(name, '')
    # designation = re.findall(designation_pattern, result)[0]
    designation = extract[1]
    result = result.replace(designation, '')
    address = ''.join(re.findall(address_pattern, result))
    result = result.replace(address, '')
    company = extract[-1]
    result = result.replace(company, '')

    # print('Email:', email)
    # print('Website:', website)
    # print('Phone:', phone)
    # print('Primary:', primary)
    # print('Secondary:', secondary)
    # print('Name:', name)
    # print('Designation:', designation)
    # print('Address:', address)
    # print('Pincode:', pincode)
    # print('company:', company)
    # print('remaining:', result)

    info = [name, designation, company, email, website, primary, secondary, address, pincode, result]
    return (info)

with st.sidebar:
    selected = option_menu(
        menu_title="Navigaton",  # required
        options=["Home","---","Upload", "View/Modify", "---", "About"],  # required
        icons=["house","", "upload","binoculars",  "", "envelope"],  # optional
        menu_icon="person-vcard",  # optional
        default_index=0,  # optional
        styles={"nav-link": {"--hover-color": "brown"}},
        orientation="vertical",
    )
if selected == 'Home':
    st.subheader("Welcome to the BizCard Project! ")
    st.markdown("__<p>We are here to introduce you to an innovative solution that will transform the way you manage "
                "your contact information. Our project is centered around simplifying the process of storing and "
                "accessing business cards by creating a digital database.</p>__ "
                "<br>"
                "__<p>Gone are the days of manually entering contact details from visiting cards. "
                "With our cutting-edge technology, all you need to do is scan the card using our integrated scanner, "
                "and voila! A soft copy of the card is created and securely stored in our database.</p>__ "
                "<br>"
                "__<p>Imagine the convenience of having all your contacts readily available at your fingertips. "
                "No more digging through stacks of business cards or struggling to remember where you put that "
                "important contact. Our system ensures that your contacts are organized and easily searchable, "
                "saving you time and effort.</p>__"
                "<br>"
                "__<p>Not only does our BizCard Project offer a streamlined approach to managing contacts, "
                "but it eliminating the need for physical storage and "
                "reducing the risk of losing important cards, our digital database ensures that your valuable "
                "connections are preserved for the long term.</p>__ "
                "<br>"
                "__<p>We understand the importance of building and nurturing relationships in the business world. "
                "That's why our project empowers you to strengthen your network efficiently. With quick access to "
                "contact information, you can reach out to potential clients, collaborators, or partners effortlessly, "
                "helping you seize every opportunity that comes your way.</p>__ "
                "<br>"
                "__<p>Join us on this journey of revolutionizing contact management. Say goodbye to cluttered desks "
                "and hello to a digital future. Explore our BizCard Project and discover the ease and efficiency of "
                "keeping your contacts in a secure, accessible, and organized format. </p>__"
                "<br>"
                "__<p>Start scanning, start connecting, and start building lasting relationships with the BizCard "
                "Project.</p>__",unsafe_allow_html=True)
elif selected == 'Upload':
    uploaded_file = st.file_uploader("Choose a image file",type=["jpg", "jpeg", "png"])
    if uploaded_file != None:
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        col1, col2, col3 = st.columns([2,1,2])
        with col3:
            st.image(image)
        with col1:
            result = reader.readtext(image, detail=0)
            info = data_extrac(result)
            #st.table(pd.Series(info, index=['Name', 'Designation', 'Company', 'Email ID', 'Website', 'Primary Contact', 'Secondary Contact', 'Address', 'Pincode', 'Other']))
            ls_name = st.text_input('Name:',info[0])
            ls_desig = st.text_input('Designation:', info[1])
            ls_Com = st.text_input('Company:', info[2])
            ls_mail = st.text_input('Email ID:', info[3])
            ls_url = st.text_input('Website:', info[4])
            ls_m1 = st.text_input('Primary Contact:', info[5])
            ls_m2 = st.text_input('Secondary Contact:', info[6])
            ls_add = st.text_input('Address:', info[7])
            ls_pin = st.number_input('Pincode:', info[8])
            ls_oth = st.text_input('Others(this will not stored):', info[9])
            a = st.button("upload")
            if a:
                guvi.execute(
                    "CREATE TABLE IF NOT EXISTS business_cards (name VARCHAR(255), designation VARCHAR(255), "
                    "company VARCHAR(255), email VARCHAR(255), website VARCHAR(255), primary_no VARCHAR(255), "
                    "secondary_no VARCHAR(255), address VARCHAR(255), pincode int, image bytea)")
                query = "INSERT INTO business_cards (name, designation, company, email, website, primary_no, secondary_no, " \
                      "address, pincode, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (ls_name, ls_desig, ls_Com, ls_mail, ls_url, ls_m1, ls_m2, ls_add, ls_pin, psycopg2.Binary(image))
                guvi.execute(query, val)
                selva.commit()
                st.success('Contact stored successfully in database', icon="✅")
elif selected == 'View/Modify':
    col1, col2, col3 = st.columns([2,2,4])
    with col1:
        guvi.execute('select name from business_cards')
        y = guvi.fetchall()
        contact = [x[0] for x in y]
        contact.sort()
        selected_contact = st.selectbox('Name',contact)
    with col2:
        mode_list = ['','View','Modify','Delete']
        selected_mode = st.selectbox('Mode',mode_list,index = 0)

    if selected_mode == 'View':
        col5,col6 = st.columns(2)
        with col5:
            guvi.execute(f"select name, designation, company, email, website, primary_no, secondary_no, "
                         f"address, pincode from business_cards where name = '{selected_contact}'")
            y = guvi.fetchall()
            st.table(pd.Series(y[0],index=['Name', 'Designation', 'Company', 'Email ID', 'Website', 'Primary Contact', 'Secondary Contact', 'Address', 'Pincode'],name='Card Info'))

    elif selected_mode == 'Modify':
        guvi.execute(f"select name, designation, company, email, website, primary_no, secondary_no, "
                     f"address, pincode from business_cards where name = '{selected_contact}'")
        info = guvi.fetchone()
        col5, col6 = st.columns(2)
        with col5:
            ls_name = st.text_input('Name:', info[0])
            ls_desig = st.text_input('Designation:', info[1])
            ls_Com = st.text_input('Company:', info[2])
            ls_mail = st.text_input('Email ID:', info[3])
            ls_url = st.text_input('Website:', info[4])
            ls_m1 = st.text_input('Primary Contact:', info[5])
            ls_m2 = st.text_input('Secondary Contact:', info[6])
            ls_add = st.text_input('Address:', info[7])
            ls_pin = st.number_input('Pincode:', info[8])
        a = st.button("Update")
        if a:
            query = f"update business_cards set name = %s, designation = %s, company = %s, email = %s, website = %s, " \
                    f"primary_no = %s, secondary_no = %s, address = %s, pincode = %s where name = '{selected_contact}'"
            val = (ls_name, ls_desig, ls_Com, ls_mail, ls_url, ls_m1, ls_m2, ls_add, ls_pin)
            guvi.execute(query, val)
            selva.commit()
            st.success('Contact updated successfully in database', icon="✅")

    elif selected_mode == 'Delete':
        st.markdown(
            f'__<p style="text-align:left; font-size: 20px; color: #FAA026">You are trying to remove {selected_contact} '
            f'contact from database.</P>__',
            unsafe_allow_html=True)
        warning_content = """
            **Warning:**
            This action will permanently delete the contact from the database and cannot be recovered. 
            Please review and confirm..
        """
        st.warning(warning_content)
        confirm = st.button('Confirm')
        if confirm:
            query = f"DELETE FROM business_cards where name = '{selected_contact}'"
            guvi.execute(query)
            selva.commit()
            st.success('Contact removed successfully from database', icon="✅")
elif selected == 'About':
    st.markdown('__<p style="text-align:left; font-size: 25px; color: #FAA026">Summary of BizCard Project</P>__',
                unsafe_allow_html=True)
    st.write("This business card project focused on enabling users to scan any visiting card and make a soft copy in "
             "the database. This innovative business card project has revolutionized the way we store contact "
             "information. With its built-in scanner, users can quickly and easily scan any visiting card into a "
             "soft copy, which can be stored in a secure database for quick access. This is an efficient and effective "
             "way to keep track of contacts and build relationships.")
    st.markdown('__<p style="text-align:left; font-size: 20px; color: #FAA026">Applications and Packages Used:</P>__',
                    unsafe_allow_html=True)
    st.write("  * Python")
    st.write("  * PostgresSql")
    st.write("  * Streamlit")
    st.write("  * Github")
    st.write("  * Pandas, EasyOCR, Re, CV2, Psycopg2")
    st.markdown('__<p style="text-align:left; font-size: 20px; color: #FAA026">For feedback/suggestion, connect with me on</P>__',
                unsafe_allow_html=True)
    st.subheader("LinkedIn")
    st.write("https://www.linkedin.com/in/selvamani-a-795580266/")
    st.subheader("Email ID")
    st.write("selvamani.ind@gmail.com")
    st.subheader("Github")
    st.write("https://github.com/selvamani1992")
    st.balloons()