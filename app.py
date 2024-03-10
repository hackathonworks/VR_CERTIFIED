from flask import Flask, request, send_file, render_template_string, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

form_html = '''
<!doctype html>
<html>
<head>
    <title>Certificate Generator</title>
</head>
<body>
    <h2>Customize Your Certificate</h2>
    <form method="post" enctype="multipart/form-data">
        <label for="title">Certificate Title:</label><br>
        <input type="text" id="title" name="title" required><br>
        <label for="name">Name:</label><br>
        <input type="text" id="name" name="name" required><br>
        <label for="event">Event Name:</label><br>
        <input type="text" id="event" name="event" required><br>
        <label for="organizer">Organizer:</label><br>
        <input type="text" id="organizer" name="organizer" required><br>
        <label for="date">Event Date:</label><br>
        <input type="date" id="date" name="date" required><br>
        <label for="logo">Logo (optional):</label><br>
        <input type="file" id="logo" name="logo"><br>
        <label for="signature">Signature (optional):</label><br>
        <input type="file" id="signature" name="signature"><br>
        <label for="bg_color">Background Color (optional):</label><br>
        <input type="color" id="bg_color" name="bg_color" value="#FFFFFF"><br>
        <label for="font_color">Font Color:</label><br>
        <input type="color" id="font_color" name="font_color" value="#000000"><br><br>
        <input type="submit" name="action" value="Preview">
        <input type="submit" name="action" value="Generate Certificate">
    </form>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        name = request.form['name']
        event = request.form['event']
        organizer = request.form['organizer']
        date = request.form['date']
        bg_color = request.form.get('bg_color', '#FFFFFF')
        font_color = request.form.get('font_color', '#000000')
        logo_file = request.files.get('logo')
        signature_file = request.files.get('signature')
        action = request.form['action']

        if action == "Preview":
            certificate_path = generate_certificate(title, name, event, organizer, date, logo_file, None, signature_file, bg_color, font_color, True)
            return redirect(url_for('static', filename=certificate_path, _external=True))
        else:
            certificate = generate_certificate(title, name, event, organizer, date, logo_file, None, signature_file, bg_color, font_color)
            return send_file(certificate, mimetype='image/jpeg', as_attachment=True, download_name='certificate.jpg')
    
    return render_template_string(form_html)

def generate_certificate(title, name, event, organizer, date, logo_file, background_file, signature_file, bg_color="#FFFFFF", font_color="#000000", preview=False):
    img = Image.new('RGB', (800, 600), color=bg_color)
    d = ImageDraw.Draw(img)
    font_path = os.path.join(app.root_path, 'arial.ttf')  # Adjust this path as needed
    font = ImageFont.truetype(font_path, 40)
    small_font = ImageFont.truetype(font_path, 30)

    # Optional: Add logo
    if logo_file:
        logo = Image.open(logo_file.stream)
        logo.thumbnail((100, 100))
        img.paste(logo, (10, 10), logo)

    # Optional: Add signature
    if signature_file:
        signature = Image.open(signature_file.stream)
        signature.thumbnail((200, 100))
        img.paste(signature, (600, 480), signature)

    d.text((400, 50), title, fill=font_color, font=font, anchor="mm")
    d.text((400, 150), f"awarded to {name}", fill=font_color, font=small_font, anchor="mm")
    d.text((400, 200), f"for participating in {event}", fill=font_color, font=small_font, anchor="mm")
    d.text((400, 250), f"Organized by {organizer}", fill=font_color, font=small_font, anchor="mm")
    d.text((400, 300), f"on {date}", fill=font_color, font=small_font, anchor="mm")

    if preview:
        preview_path = "preview_certificate.jpg"
        img.save(os.path.join(app.static_folder, preview_path))
        return preview_path
    else:
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=70)
        img_io.seek(0)
        return img_io

#if __name__ == '__main__':
#    app.run(debug=True)
