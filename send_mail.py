
from email import encoders
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase


smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = "siyamak1981@gmail.com"
# body = """  Hi I'm Siyamak
#             I hope you are doing well
#             Full Stack Web Developer with 4 years of practical experience in object-oriented programing and design patterns and extensive experience with PHP and Python.
#             Proven ability in optimizing web functionality that improve data retrieval and workflow efficiencies.
#             I am interested in new and hard challenges and an interest in teamwork.
#             Are there opportunity for me in your company?
#             For more information please download my resume on below or contact with me
#             http://s-abasnezhad.ir
#             whatsapp:+989198859723
#         """
html = """\
  <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css?family=Merriweather|Lato" rel="stylesheet">
    <style>
        body {
            font-family: 'Lato', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #dee7ef;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #181717;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        h1 {
            font-family: 'Merriweather', serif;
            color: #48da9b;
            border-bottom: 2px solid #5a67d8;
            padding-bottom: 10px;
        }
        h3 {
            color: #5a67d8;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
        a {
            color: #5a67d8;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .footer {
            margin-top: 20px;
            font-size: 12px;
            text-align: center;
            color: #e4e3e8;
        }
        .contact-info {
            background-color: #48da9b;
            color: #e4e3e8;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .profile-image {
            width: 100%; /* Adjust width as needed */
            height: auto; /* Maintain aspect ratio */
            border-radius: 50%; /* Make it circular if it's a profile picture */
            margin-bottom: 20px; /* Space below the image */
        }
       div.container img {
            width:200px;
            height: 200px;
            float: right;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://schoolofinternetmarketing.co.in/wp-content/uploads/2019/02/383x2621-1-min.jpg" alt="Profile Image" class="profile-image"> <!-- Replace with your image URL -->
        <h1>Hello!</h1>
        
        <p>I hope this message finds you well. My name is <strong>Siyamak Abasnezhad Torki</strong>, and I am a passionate Data Scientist and Full Stack Developer with over a decade of experience in software development.</p>

        <p>Throughout my career, I have developed a range of applications and solutions that leverage cutting-edge technologies to solve complex problems. My expertise spans <strong>Python, Django, Vue, TypeScript</strong> and various data science libraries, which I have used to create impactful projects such as IoT systems and AI-driven applications.</p>

        <p>I am always eager to connect with like-minded professionals and explore new opportunities for collaboration. If you are interested in discussing potential projects or sharing insights, I would love to hear from you!</p>

        <p>Thank you for your time, and I look forward to the possibility of working together.</p>

        <h3>Best Regards,<br>Siyamak Abasnezhad Torki</h3>
        
        <div class="contact-info">
            <p>Email: <a href="mailto:pydevcasts@gmail.com">pydevcasts@gmail.com</a></p>
            <p>Phone: (+98) 930 494 3348</p>
            <p>GitHub: <a href="https://github.com/pydevcasts">github.com/pydevcasts</a></p>
            <p>LinkedIn: <a href="https://www.linkedin.com/in/pydevcasts/">linkedin.com/in/pydevcasts</a></p>
        </div>
    </div>
    
    <div class="footer">
        <p>This email is intended for you. If you received this email in error, please contact me directly.</p>
    </div>
</body>
</html>

    """
password = input("what is your password of your email? ")


context = ssl.create_default_context()
with open("Emails/SaveEmail.txt", 'r') as f:
    emlist = f.readlines()
try:
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()  # Can be omitted
    server.starttls(context=context)  # Secure the connection
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)

    for email in emlist:
        receiver_email = email
        message = MIMEMultipart("alternative")
        message["Subject"] = "Data Scientist | Full Stack Developer"
        message["From"] = sender_email
        message["To"] = receiver_email
        print(message["To"])
        message["Bcc"] = receiver_email
        message.attach(MIMEText(html, "html"))

        filename="./DataScientist-CV.pdf"
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        message.attach(part)
        text = message.as_string()
        part1 = MIMEText(text, "plain")
        message.attach(part1)

        server.sendmail(sender_email, receiver_email, message.as_string())
except Exception as e:
    print(e)
finally:
    print("whole of them is done good luck!")
    server.quit()
