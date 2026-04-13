import os
import qrcode
from flask import current_app


def generate_ticket_qr(ticket_code, ticket_id):
    """
    Generate a QR code PNG for a ticket and save it to the uploads folder.

    The QR encodes:  EVENTHUB:{ticket_code}:{ticket_id}
    A scanner reads this string to verify the ticket at the door.

    Returns the filename of the saved image (e.g. 'qr_abc123.png').
    """
    qr_data = f"EVENTHUB:{ticket_code}:{ticket_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Dark purple fill on white background
    img = qr.make_image(fill_color="#1a1a2e", back_color="white")

    filename = f"qr_{ticket_code}.png"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    img.save(filepath)

    return filename
