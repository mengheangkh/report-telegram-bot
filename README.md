# Telegram Report Bot

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version 1.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/telethon-1.34+-orange.svg" alt="Telethon 1.34+">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License MIT">
</p>

<p align="center">
  <b>Telegram Report Bot - ប្រព័ន្ធរាយការណ៍ឆានែល Telegram ដោយស្វ័យប្រវត្តិ (គ្មានដែនកំណត់)</b>
</p>

<p align="center">
  <a href="#អំពី-ប្រព័ន្ធ">អំពីប្រព័ន្ធ</a> •
  <a href="#លក្ខណៈពិសេស">លក្ខណៈពិសេស</a> •
  <a href="#ការដំឡើង">ការដំឡើង</a> •
  <a href="#ការប្រើប្រាស់">ការប្រើប្រាស់</a> •
  <a href="#ពាក្យបញ្ជា">ពាក្យបញ្ជា</a> •
  <a href="#រចនាសម្ព័ន្ធគម្រោង">រចនាសម្ព័ន្ធ</a> •
  <a href="#អាជ្ញាប័ណ្ណ">អាជ្ញាប័ណ្ណ</a>
</p>

---

## អំពីប្រព័ន្ធ

**Telegram Report Bot** គឺជា bot ដ៏មានឥទ្ធិពលសម្រាប់រាយការណ៍ឆានែល Telegram ដែលបំពានច្បាប់។ វាអនុញ្ញាតឱ្យអ្នកប្រើប្រាស់គណនីច្រើនដើម្បីរាយការណ៍ឆានែលគោលដៅដោយស្វ័យប្រវត្តិ ដោយគ្មានដែនកំណត់ចំនួនដង។

បង្កើតឡើងដោយ [@mengheang25](https://t.me/mengheang25)

---

## លក្ខណៈពិសេស

- ✅ **គ្មានដែនកំណត់** - អាចរាយការណ៍បានច្រើនដងតាមចិត្ត
- 👥 **គាំទ្រគណនីច្រើន** - ប្រើគណនី Telegram ច្រើនក្នុងពេលតែមួយ
- 📊 **បង្ហាញវឌ្ឍនភាព** - មើលវឌ្ឍនភាពរាយការណ៍តាមពេលជាក់ស្តែង
- 🔐 **សុវត្ថិភាពខ្ពស់** - រក្សាទុក session ដោយសុវត្ថិភាព
- 🌐 **ចំណុចប្រទាក់ជាភាសាខ្មែរ** - ងាយស្រួលប្រើសម្រាប់អ្នកប្រើប្រាស់ខ្មែរ
- 📱 **គ្រប់គ្រងគណនី** - បន្ថែម លុប និងមើលបញ្ជីគណនីបាន
- ⏱ **គណនាពេលវេលា** - ប៉ាន់ស្មានពេលវេលាដែលត្រូវការ
- 📋 **មូលហេតុរាយការណ៍ច្រើន** - ជ្រើសរើសមូលហេតុផ្សេងៗគ្នា

### មូលហេតុដែលអាចរាយការណ៍បាន:
| លេខ | មូលហេតុ | ការពិពណ៌នា |
|------|-----------|----------------|
| 1 | spam | សារឥតបានការ |
| 2 | fake_account | គណនីក្លែងក្លាយ |
| 3 | violence | អំពើហិង្សា |
| 4 | child_abuse | រំលោភបំពានកុមារ |
| 5 | pornography | រូបភាពអាសអាភាស |
| 6 | geoirrelevant | មិនពាក់ព័ន្ធនឹងភូមិសាស្ត្រ |

---

## ការដំឡើង

### តម្រូវការជាមុន
- Python 3.8 ឬខ្ពស់ជាងនេះ
- Telegram API ID និង API Hash (ទទួលបានពី https://my.telegram.org)
- Bot Token ពី [@BotFather](https://t.me/botfather)

### ជំហានដំឡើង

1. **Clone គម្រោង**
```bash
git clone https://github.com/mengheangkh/report-telegram-bot
cd report-telegram-bot
python bot_repot.py