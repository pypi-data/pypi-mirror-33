import os
import jinja2
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")

class AviSendGridClient(sendgrid.SendGridAPIClient):

    def __init__(self, apikey, images_uri):
        super(AviSendGridClient, self).__init__(apikey=apikey)
        self.images_uri = images_uri
        self.jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
            trim_blocks=True,
        )

    def send_activation_email(self, from_email, to_email, first_name, activation_link):
        variables = {
            'first_name': first_name,
            'username': to_email,
            'activation_link': activation_link,
            'images_uri': self.images_uri,
        }
        template = self.jinja2_env.get_template("activation_email.template")
        from_email = Email(from_email)
        to_email = Email(to_email)
        subject = "Avi Networks SaaS account activation"
        content = Content("text/html", template.render(variables))
        mail = Mail(from_email, subject, to_email, content)
        response = self.client.mail.send.post(request_body=mail.get())
        return response.status_code
