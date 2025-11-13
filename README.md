# ESP32 Flasher Tool

โปรแกรม Python สำหรับ burn/flash ไฟล์ binary ลง ESP32 board ผ่าน GUI ที่ใช้งานง่าย

## ฟีเจอร์

- ✅ เลือก COM Port พร้อมปุ่ม Refresh
- ✅ เลือกไฟล์ Binary ทั้ง 4 ไฟล์:
  - `bootloader.bin` (ตำแหน่ง 0x1000)
  - `partitions.bin` (ตำแหน่ง 0x8000)
  - `boot_app0.bin` (ตำแหน่ง 0xe000)
  - `LoRaController.ino.bin` (ตำแหน่ง 0x10000)
- ✅ หา esptool.exe อัตโนมัติ หรือเลือกเองได้
- ✅ แสดงสถานะการ flash แบบ real-time
- ✅ Browse ไฟล์เริ่มที่ directory ปัจจุบัน

## ความต้องการของระบบ

- Python 3.6 หรือสูงกว่า
- Windows (รองรับ Linux/macOS ด้วยการปรับ path)
- ESP32 board พร้อม USB cable
- esptool.exe หรือ esptool.py

## การติดตั้ง

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

หรือติดตั้งแยก:

```bash
pip install pyserial
```

### 2. ติดตั้ง esptool (ถ้ายังไม่มี)

**วิธีที่ 1: ติดตั้งผ่าน pip (แนะนำ)**
```bash
pip install esptool
```

**วิธีที่ 2: ใช้ esptool.exe จาก Arduino**
- ติดตั้ง Arduino IDE และ ESP32 board package
- esptool.exe จะอยู่ใน path: `Documents\Arduino\hardware\heltec\esp32\tools\esptool\esptool.exe`
- หรือ `Documents\Arduino\hardware\espressif\esp32\tools\esptool\esptool.exe`

## วิธีการใช้งาน

### 1. รันโปรแกรม

```bash
python main.py
```

### 2. เลือก COM Port

- กดปุ่ม **Refresh** เพื่อ refresh COM ports ที่มี
- เลือก COM port ที่ ESP32 board เชื่อมต่ออยู่

### 3. เลือก ESP Tool Path (ถ้าจำเป็น)

- โปรแกรมจะพยายามหา esptool.exe อัตโนมัติ
- ถ้าไม่พบ จะแสดง "Not found" สีแดง
- กดปุ่ม **Browse** เพื่อเลือก esptool.exe หรือ esptool.py เอง

### 4. เลือกไฟล์ Binary

กดปุ่ม **Browse** สำหรับแต่ละไฟล์:

- **Bootloader.bin (0x1000)**: ไฟล์ bootloader
- **Partitions.bin (0x8000)**: ไฟล์ partitions table
- **boot_app0.bin (0xe000)**: ไฟล์ boot app0
- **LoRaController.ino.bin (0x10000)**: ไฟล์ application binary

> **หมายเหตุ**: เมื่อเลือกไฟล์แล้ว ครั้งต่อไปจะเริ่มที่ directory ของไฟล์ที่เลือกล่าสุด

### 5. Flash ESP32

- ตรวจสอบให้แน่ใจว่าได้เลือก:
  - COM Port
  - ESP Tool Path
  - ไฟล์ Binary ทั้ง 4 ไฟล์
- กดปุ่ม **Flash ESP32** เพื่อเริ่ม burn
- รอให้กระบวนการ flash เสร็จสิ้น
- ดูผลลัพธ์ในหน้าต่าง Status

## ตัวอย่างการใช้งาน

```
1. เชื่อมต่อ ESP32 board เข้ากับคอมพิวเตอร์
2. เปิดโปรแกรม ESP32 Flasher
3. เลือก COM Port (เช่น COM7)
4. เลือกไฟล์ binary ทั้ง 4 ไฟล์
5. กด Flash ESP32
6. รอจนเสร็จสิ้น
```

## โครงสร้างไฟล์

```
Binary/
├── Master/
│   ├── main.py              # โปรแกรมหลัก
│   ├── requirements.txt     # Dependencies
│   ├── README.md           # คู่มือนี้
│   ├── boot_app0.bin       # ไฟล์ binary (ตัวอย่าง)
│   ├── LoRaController.ino.bootloader.bin
│   ├── LoRaController.ino.partitions.bin
│   └── LoRaController.ino.bin
```

## การแก้ไขปัญหา

### esptool.exe ไม่พบ

**วิธีแก้:**
1. ติดตั้ง esptool ผ่าน pip: `pip install esptool`
2. หรือกดปุ่ม Browse เพื่อเลือก esptool.exe จาก Arduino installation
3. หรือดาวน์โหลด esptool.py จาก GitHub

### COM Port ไม่แสดง

**วิธีแก้:**
1. ตรวจสอบว่า ESP32 board เชื่อมต่อแล้ว
2. ติดตั้ง USB driver สำหรับ ESP32
3. กดปุ่ม Refresh อีกครั้ง
4. ตรวจสอบใน Device Manager ว่า board ถูกตรวจจับ

### Flash ล้มเหลว

**วิธีแก้:**
1. ตรวจสอบว่า COM port ถูกต้อง
2. ตรวจสอบว่าไฟล์ binary ครบถ้วนและถูกต้อง
3. ลองกดปุ่ม Reset บน ESP32 board ก่อน flash
4. ลด baud rate (แก้ไขในโค้ดจาก 921600 เป็น 115200)

### Permission Denied

**วิธีแก้:**
- รันโปรแกรมด้วยสิทธิ์ Administrator (Windows)
- หรือใช้ `sudo` (Linux/macOS)

## พารามิเตอร์ Flash

โปรแกรมใช้พารามิเตอร์ต่อไปนี้:

- **Chip**: ESP32
- **Baud Rate**: 921600
- **Flash Mode**: keep
- **Flash Frequency**: keep
- **Flash Size**: keep

## หมายเหตุ

- โปรแกรมจะเริ่ม browse ที่ directory ปัจจุบัน (directory ที่มีไฟล์ script)
- ถ้าเลือกไฟล์แล้ว ครั้งต่อไปจะเริ่มที่ directory ของไฟล์ที่เลือกล่าสุด
- โปรแกรมจะพยายามหา esptool.exe อัตโนมัติจากหลาย path
- รองรับทั้ง esptool.exe และ esptool.py

## License

โปรแกรมนี้สร้างขึ้นเพื่อใช้งานภายในโครงการ Thermite v4

## ผู้พัฒนา

สร้างด้วย Python และ tkinter

---

**คำเตือน**: ตรวจสอบให้แน่ใจว่าไฟล์ binary ที่ใช้ถูกต้องก่อน flash เพื่อหลีกเลี่ยงการทำให้ board เสียหาย

