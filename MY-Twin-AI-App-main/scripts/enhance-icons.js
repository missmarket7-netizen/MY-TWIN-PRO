const sharp = require('sharp');
const path = require('path');

const iconInput = path.join(__dirname, '..', 'assets', 'icon.png');
const adaptiveInput = path.join(__dirname, '..', 'assets', 'adaptive-icon.png');

async function enhance() {
  try {
    // 1. تحسين icon.png (1024x1024)
    const icon = sharp(iconInput);
    const iconMetadata = await icon.metadata();
    
    // إنشاء نسخة محسنة: زيادة التشبع + ظل ناعم
    await icon
      .modulate({ saturation: 1.2, brightness: 1.05 })
      .resize(1024, 1024)
      .png()
      .toFile(iconInput.replace('.png', '_enhanced.png'));
    
    console.log('✅ Enhanced icon saved as icon_enhanced.png');

    // 2. تحسين adaptive-icon.png (432x432)
    // جعل الخلفية الأمامية أكثر وضوحًا مع إطار دائري
    const size = 432;
    const padding = 48; // مساحة الأيقونة داخل الدائرة
    
    await sharp({
      create: {
        width: size,
        height: size,
        channels: 4,
        background: { r: 0, g: 0, b: 0, alpha: 0 }
      }
    })
    .composite([
      {
        input: await sharp(adaptiveInput)
          .resize(size - padding * 2, size - padding * 2)
          .png()
          .toBuffer(),
        top: padding,
        left: padding
      }
    ])
    .png()
    .toFile(adaptiveInput.replace('.png', '_enhanced.png'));
    
    console.log('✅ Enhanced adaptive icon saved as adaptive-icon_enhanced.png');
    console.log('📝 Replace original files after review:');
    console.log('   cp assets/icon_enhanced.png assets/icon.png');
    console.log('   cp assets/adaptive-icon_enhanced.png assets/adaptive-icon.png');
  } catch (err) {
    console.error('❌ Enhancement failed:', err.message);
  }
}

enhance();
