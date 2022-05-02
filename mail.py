import smtplib,getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class successMail:
    def __init__(self) -> None:
        self.sender_address = 'idealabsjec@gmail.com'
        self.sender_password = 'idealabsjec2022'
        self.receiver_address = []

    def addRecipent(self, address):
        self.receiver_address.append(address)


    def sendMail(self,name, usn, purpose, start, end):
        # msg = 'Test Mail works'
        mail_content_html =f'''
        <html>
        <head>
            <h1> Slot Booked </h1>
            <h3><p>Hello {name}</p>
            <p>You have booked {purpose} to be used from {start} to {end} </p>
            <br>
            <p><b>Thank You</b></p></h3>
            <br>
            <h4>Regards</h4>
            <h4>IdeaLab Sjec</h4>
        '''

        message = MIMEMultipart("alternative")
        message['From'] = self.sender_address
        message['Subject'] = "Hello world"
        message.attach(MIMEText(mail_content_html, 'html'))

        try:
            session = smtplib.SMTP('smtp.gmail.com',587) #gmail with port
            session.starttls() #enable security
            session.login(self.sender_address,self.sender_password)

            text=message.as_string()
            session.sendmail(self.sender_address, self.receiver_address, text)
            session.quit()
            print('Mail Sent')

        except Exception as e:
            print(e)





# ----------------------------------------------------------
#user credentials
# sender_address = 'idealabsjec@gmail.com'
# print("Enter password")
# password is `idealabsjec2022`
# sender_pass = 'idealabsjec2022'
# receiver_address = ['justpk88@gmail.com'] 

# msg = 'Test Mail works'
# mail_content_html =f'''
# <html>
# <head>
#     <h1> Hello world </h1>
#     <p>{msg}</p>
# '''

# message = MIMEMultipart("alternative")
# message['From'] = sender_address
# message['Subject'] = "Hello world"
# message.attach(MIMEText(mail_content_html, 'html'))

# try:
#     session = smtplib.SMTP('smtp.gmail.com',587) #gmail with port
#     session.starttls() #enable security
#     session.login(sender_address,sender_pass)

#     text=message.as_string()
#     session.sendmail(sender_address, receiver_address, text)
#     session.quit()
#     print('Mail Sent')

# except Exception as e:
#     print(e)