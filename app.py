from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
import io

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
        <label for="background">Certificate Background (optional):</label><br>
        <input type="file" id="background" name="background"><br><br>
        <input type="submit" value="Generate Certificate">
    </form>
</body>
</html>
'''
def generate_certificate(title, name, event, organizer, date, logo_file, background_file):
    # Load background image or create a blank image
    if background_file and 'background' in request.files:
        background = Image.open(request.files['background'].stream)
        img = background.convert('RGB')
    else:
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))

    d = ImageDraw.Draw(img)
    font_path = "arial.ttf"  # Adjust this path as needed
    font = ImageFont.truetype(font_path, 40)
    small_font = ImageFont.truetype(font_path, 30)

    # Optional: Add logo
    if logo_file and 'logo' in request.files:
        logo = Image.open(request.files['logo'].stream)
        img.paste(logo, (10, 10))

    # Text positions
    title_pos = (400, 100)
    name_pos = (400, 200)
    event_pos = (400, 250)
    organizer_pos = (400, 300)
    date_pos = (400, 350)

    # Text colors
    title_color = (0, 0, 128)  # Navy
    text_color = (0, 102, 204)  # Lighter blue

    # Drawing text
    d.text(title_pos, title, fill=title_color, font=font, anchor="mm")
    d.text(name_pos, f"awarded to {name}", fill=text_color, font=small_font, anchor="mm")
    d.text(event_pos, f"for participating in {event}", fill=text_color, font=small_font, anchor="mm")
    d.text(organizer_pos, f"Organized by {organizer}", fill=text_color, font=small_font, anchor="mm")
    d.text(date_pos, f"on {date}", fill=text_color, font=small_font, anchor="mm")

    # Save the image to a bytes buffer
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    
    return img_io
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        name = request.form['name']
        event = request.form['event']
        organizer = request.form['organizer']
        date = request.form['date']
        logo_file = request.files.get('logo')  # Optional
        background_file = request.files.get('background')  # Optional

        certificate = generate_certificate(title, name, event, organizer, date, logo_file, background_file)
        return send_file(certificate, mimetype='image/jpeg', as_attachment=True, download_name='certificate.jpg')
    return render_template_string(form_html)

