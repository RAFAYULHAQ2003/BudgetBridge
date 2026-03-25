from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Invoice, ProjectPaymentInvoice


@shared_task
def send_invoice_email(invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)

    
    if invoice.invoice_sent:
        return "Already sent"

    html_content = render_to_string(
        "finance/email_invoice.html",
        {
            "invoice": invoice,
            "invoice_items": invoice.items.all(),
            "company": invoice.company,
            "client": invoice.client,
        }
    )

    subject = f"Invoice #{invoice.invoice_no} for Project: {invoice.project.name}"
    from_email = "noreply@budgetbridge.com"
    to_email = [invoice.client.email]

    email = EmailMultiAlternatives(subject, "", from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)

    
    invoice.invoice_sent = True
    invoice.save()

@shared_task
def send_payment_invoice_email(invoice_id):
    try:
        invoice = ProjectPaymentInvoice.objects.get(id=invoice_id)
    except ProjectPaymentInvoice.DoesNotExist:
        return f"Invoice {invoice_id} not found."

    if invoice.invoice_sent:
        return "Already sent"

    # Render the email content using the new detailed template
    html_content = render_to_string(
        "finance/email_payment_invoice.html",
        {
            "invoice": invoice,
            "client": invoice.project.client,
        }
    )

    # Email details
    subject = f"Invoice #{invoice.invoice_no} for Project: {invoice.project.name}"
    from_email = "noreply@budgetbridge.com"
    to_email = [invoice.project.client.email]

    # Send the email
    email = EmailMultiAlternatives(subject, "", from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)

    # Mark invoice as sent
    invoice.invoice_sent = True
    invoice.save()

    return f"Invoice {invoice.invoice_no} sent successfully."