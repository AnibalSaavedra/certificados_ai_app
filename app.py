
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import io, os, requests

# Configuración general
st.set_page_config(page_title="Certificados AI - CRB", page_icon="🤖", layout="centered")

# Descargar fuente Montserrat si no existe
font_path = "Montserrat-SemiBold.ttf"
if not os.path.exists(font_path):
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-SemiBold.ttf"
        r = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(r.content)
    except Exception:
        font_path = None

# --- Página 1: Bienvenida ---
if "aceptado" not in st.session_state:
    st.session_state.aceptado = False

if not st.session_state.aceptado:
    st.title("🤖 Bienvenidos")
    st.subheader("De la gestión manual a la automatización total:")
    st.write("**Liderazgo profesional y uso de inteligencia artificial en procesos de calidad del laboratorio clínico**")
    st.markdown("---")
    st.info("Los datos ingresados **no serán almacenados**, solo se utilizarán para generar el certificado sin dejar registro.")

    aceptar = st.checkbox("He leído y acepto los términos y condiciones para generar mi certificado.")
    if aceptar:
        st.session_state.aceptado = True
        st.rerun()

# --- Página 2: Generación de Certificado ---
else:
    st.markdown("<h2 style='text-align:center;'>🧾 Generación de Certificado</h2>", unsafe_allow_html=True)
    nombre = st.text_input("Ingresa tu nombre completo:", "")

    generar = st.button("📜 Generar Certificado")

    if generar and nombre.strip():
        # Buscar imagen base
        if os.path.exists("certificado_base.jpg"):
            base_image = Image.open("certificado_base.jpg").convert("RGBA")
        elif os.path.exists("certificado_base.png"):
            base_image = Image.open("certificado_base.png").convert("RGBA")
        else:
            st.error("❌ No se encontró la imagen base. Asegúrate de tener 'certificado_base.jpg' o 'certificado_base.png' en la carpeta del proyecto.")
            st.stop()

        texto = nombre.strip().upper()
        W, H = base_image.size

        # Crear capa para texto
        text_layer = Image.new("RGBA", (W//2, H//4), (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_layer)

        # Fuente base grande
        font_size = int(H * 0.15)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        # Calcular tamaño texto
        try:
            bbox = draw.textbbox((0, 0), texto, font=font)
            w_text, h_text = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            w_text, h_text = draw.textlength(texto, font=font), font_size

        pos_x = (text_layer.width - w_text) / 2
        pos_y = (text_layer.height - h_text) / 2
        draw.text((pos_x, pos_y), texto, fill=(0, 0, 0, 255), font=font)

        # Escalar el texto 3×
        scale_factor = 3
        text_layer_large = text_layer.resize(
            (text_layer.width * scale_factor, text_layer.height * scale_factor),
            resample=Image.LANCZOS
        )

        # Centrar sobre el diploma
        tx, ty = text_layer_large.size
        px = (W - tx) // 2
        py = (H - ty) // 2

        # Fusionar
        base_image.alpha_composite(text_layer_large, dest=(px, py))

        # Guardar y PDF
        temp_img = "temp_certificado.jpg"
        base_image.convert("RGB").save(temp_img, "JPEG")
        pdf = FPDF("L", "mm", "A4")
        pdf.add_page()
        pdf.image(temp_img, x=0, y=0, w=297, h=210)
        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.success("✅ Certificado generado correctamente con texto grande visible.")
        st.download_button(
            label="📥 Descargar certificado en PDF",
            data=pdf_bytes,
            file_name=f"Certificado_{nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

        if os.path.exists(temp_img):
            os.remove(temp_img)
