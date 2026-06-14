const sharp = require('sharp');
const path = require('path');

const inputIcon = path.join(__dirname, '..', 'assets', 'icon.png');
const outputIcon = path.join(__dirname, '..', 'assets', 'notification-icon.png');

async function generate() {
  try {
    const image = sharp(inputIcon);
    
    // إنشاء أيقونة إشعارات: 96x96، خلفية شفافة، أيقونة بيضاء في المنتصف
    await image
      .resize(96, 96, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .threshold(128)       // تحويل المناطق الداكنة إلى أبيض
      .negate({ alpha: false }) // عكس الألوان (لجعل الأيقونة بيضاء)
      .png()
      .toFile(outputIcon);

    console.log('✅ Notification icon created: assets/notification-icon.png');
  } catch (err) {
    console.error('❌ Failed:', err.message);
  }
}

generate();
