# Telegram Report Bot - Complete Working Version (No Report Limit)
# បង្កើតឡើងដោយ @mengheang25


import logging
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam, 
    InputReportReasonViolence, 
    InputReportReasonPornography, 
    InputReportReasonChildAbuse,
    InputReportReasonOther,
    InputReportReasonFake
)
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError, FloodWaitError
from os import listdir, mkdir, path, remove
from re import search
import asyncio
import time
import sys

# ========== ការកំណត់រចនាសម្ព័ន្ធ ==========
BOT_TOKEN = '8429770147:AAEVNAIi3sD_3Ne3LubJFf7Kp_QSOTodRcc'
API_ID = 25148883
API_HASH = 'abc30c3b47a075ec9a0854b3015ef210'
OWNER_ID = 1911793084

# ========== បង្កើតថតឯកសារ ==========
try:
    mkdir('sessions')
    mkdir('logs')
except:
    pass

# ========== កំណត់រចនាសម្ព័ន្ធ logging ==========
logging.basicConfig(
    filename='logs/bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== បញ្ជីមូលហេតុសម្រាប់រាយការណ៍ ==========
REPORT_REASONS = {
    1: {'name': 'spam', 'display': 'សារឥតបានការ'},
    2: {'name': 'fake_account', 'display': 'គណនីក្លែងក្លាយ'},
    3: {'name': 'violence', 'display': 'អំពើហិង្សា'},
    4: {'name': 'child_abuse', 'display': 'រំលោភបំពានកុមារ'},
    5: {'name': 'pornography', 'display': 'រូបភាពអាសអាភាស'},
    6: {'name': 'geoirrelevant', 'display': 'មិនពាក់ព័ន្ធនឹងភូមិសាស្ត្រ'}
}

# ========== កំណត់ Reason Classes សម្រាប់ ReportPeerRequest ==========
REASON_CLASSES = {
    'spam': InputReportReasonSpam(),
    'fake_account': InputReportReasonFake(),
    'violence': InputReportReasonViolence(),
    'child_abuse': InputReportReasonChildAbuse(),
    'pornography': InputReportReasonPornography(),
    'geoirrelevant': InputReportReasonOther()
}

# ========== អថេរសម្រាប់រក្សាទុកស្ថានភាពអ្នកប្រើ ==========
USER_STATES = {}
USER_DATA = {}
USER_SESSIONS = {}

# ========== បង្កើត Bot Client ==========
bot = TelegramClient('bot_session', API_ID, API_HASH)

# ==================== ព្រឹត្តិការណ៍ /start ====================
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    
    # ផ្លូវទៅកាន់រូបភាព (ត្រូវដាក់រូបភាពក្នុងថតដូចគ្នាជាមួយកូដ)
    image_path = 'start_image.png'  # ឈ្មោះឯកសាររូបភាព
    
    buttons = [
        [Button.url('👨‍💻 Developer', 'https://t.me/mengheang25')],
        [Button.inline('📢 Reporter', b'reporter')]
    ]
    
    welcome_message = (
        "🌟 **សូមស្វាគមន៍មកកាន់ Telegram Report Bot** 🌟\n\n"
        "Bot នេះជួយអ្នកក្នុងការរាយការណ៍ឆានែល Telegram ដែលបំពានច្បាប់។\n"
        "ចុចប៊ូតុងខាងក្រោមដើម្បីចាប់ផ្តើម។\n\n"
        f"**លេខសម្គាល់របស់អ្នក:** `{user_id}`"
    )
    
    try:
        # ព្យាយាមផ្ញើរូបភាពជាមួយសារ
        await event.respond(
            welcome_message,
            file=image_path,
            buttons=buttons,
            parse_mode='md'
        )
    except:
        # បើរកមិនឃើញរូបភាព ឬមានបញ្ហា ផ្ញើតែសារធម្មតា
        await event.respond(welcome_message, buttons=buttons, parse_mode='md')

# ==================== ព្រឹត្តិការណ៍ Callback Query ====================
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user_id = event.sender_id
    data = event.data.decode()
    
    if data == 'reporter':
        USER_STATES[user_id] = 'waiting_for_target'
        USER_DATA[user_id] = {}
        
        session_files = [f for f in listdir('sessions') if f.endswith('.session')]
        
        if not session_files:
            await event.edit(
                "❌ **រកមិនឃើញគណនី!**\n\n"
                "សូមបន្ថែមគណនីជាមុនសិនដោយប្រើពាក្យបញ្ជា `/add_account`។\n\n"
                "ទម្រង់: `/add_account +1234567890`",
                parse_mode='md'
            )
            del USER_STATES[user_id]
            del USER_DATA[user_id]
            return
        
        await event.edit(
            "📢 **កំណត់រចនាសម្ព័ន្ធឆានែលគោលដៅ**\n\n"
            "សូមបញ្ចូលឈ្មោះអ្នកប្រើឆានែលគោលដៅ (ដោយគ្មាន @):\n\n"
            "ឧទាហរណ៍: `telegram`",
            parse_mode='md'
        )
    
    elif data.startswith('reason_'):
        reason_num = int(data.split('_')[1])
        reason_data = REPORT_REASONS[reason_num]
        USER_DATA[user_id]['reason'] = reason_data['name']
        USER_DATA[user_id]['reason_display'] = reason_data['display']
        
        await event.edit(
            f"✅ បានជ្រើសរើសមូលហេតុ: **{reason_data['display']}**\n\n"
            "ឥឡូវសូមបញ្ចូលចំនួនដងដែលត្រូវរាយការណ៍ (អាចបញ្ចូលប៉ុន្មានក៏បាន):\n"
            "ឧទាហរណ៍: 100, 500, 1000, 5000...",
            parse_mode='md'
        )
        USER_STATES[user_id] = 'waiting_for_reports_count'
    
    elif data == 'start_report':
        await start_reporting(event)
    
    elif data == 'cancel':
        if user_id in USER_STATES:
            del USER_STATES[user_id]
        if user_id in USER_DATA:
            del USER_DATA[user_id]
        await event.edit("❌ បានបោះបង់ការរាយការណ៍។")

# ==================== ព្រឹត្តិការណ៍សារទូទៅ ====================
@bot.on(events.NewMessage)
async def message_handler(event):
    user_id = event.sender_id
    message = event.message.text.strip()
    
    if user_id in USER_SESSIONS:
        await handle_verification_code(event)
        return
    
    if user_id not in USER_STATES:
        return
    
    current_state = USER_STATES[user_id]
    
    if current_state == 'waiting_for_target':
        target = message.replace('@', '').replace('https://t.me/', '').replace('/', '').strip()
        
        if not target:
            await event.respond("❌ សូមបញ្ចូលឈ្មោះឆានែលឱ្យបានត្រឹមត្រូវ។")
            return
        
        USER_DATA[user_id]['target'] = target
        
        reasons_text = "**មូលហេតុដែលអាចរាយការណ៍បាន:**\n\n"
        for num, reason in REPORT_REASONS.items():
            reasons_text += f"{num}. {reason['display']}\n"
        
        buttons = []
        for num, reason in REPORT_REASONS.items():
            buttons.append([Button.inline(f"{num}. {reason['display']}", f"reason_{num}".encode())])
        
        buttons.append([Button.inline("❌ បោះបង់", b'cancel')])
        
        await event.respond(
            reasons_text + "\nសូមជ្រើសរើសមូលហេតុនៃការរាយការណ៍៖",
            buttons=buttons,
            parse_mode='md'
        )
        USER_STATES[user_id] = 'waiting_for_reason'
    
    elif current_state == 'waiting_for_reports_count':
        try:
            count = int(message)
            if count > 0:
                USER_DATA[user_id]['count'] = count
                
                # គណនាពេលវេលាប៉ាន់ស្មាន
                session_count = len([f for f in listdir('sessions') if f.endswith('.session')])
                total_reports = session_count * count
                estimated_time = total_reports * 0.5  # 0.5 វិនាទីក្នុងមួយដង
                
                hours = int(estimated_time // 3600)
                minutes = int((estimated_time % 3600) // 60)
                seconds = int(estimated_time % 60)
                
                time_text = ""
                if hours > 0:
                    time_text += f"{hours} ម៉ោង "
                if minutes > 0:
                    time_text += f"{minutes} នាទី "
                time_text += f"{seconds} វិនាទី"
                
                summary = (
                    f"**សេចក្តីសង្ខេបនៃការរាយការណ៍** 📋\n\n"
                    f"📢 ឆានែលគោលដៅ: @{USER_DATA[user_id].get('target')}\n"
                    f"🔢 ចំនួនដងក្នុងមួយគណនី: {count:,}\n"
                    f"👥 ចំនួនគណនី: {session_count}\n"
                    f"📊 សរុបទាំងអស់: {total_reports:,} ដង\n"
                    f"⏱ ពេលប៉ាន់ស្មាន: {time_text}\n"
                    f"📋 មូលហេតុ: {USER_DATA[user_id].get('reason_display')}\n\n"
                    "ចុចប៊ូតុងខាងក្រោមដើម្បីចាប់ផ្តើមរាយការណ៍!"
                )
                
                await event.respond(
                    summary,
                    buttons=[
                        [Button.inline("🚀 ចាប់ផ្តើមរាយការណ៍", b'start_report')],
                        [Button.inline("❌ បោះបង់", b'cancel')]
                    ],
                    parse_mode='md'
                )
                USER_STATES[user_id] = 'ready_to_report'
            else:
                await event.respond("❌ សូមបញ្ចូលចំនួនដងធំជាង 0:")
        except ValueError:
            await event.respond("❌ សូមបញ្ចូលលេខឱ្យបានត្រឹមត្រូវ:")

# ==================== ដោះស្រាយការបញ្ចូលលេខកូដផ្ទៀងផ្ទាត់ ====================
async def handle_verification_code(event):
    user_id = event.sender_id
    message = event.message.text.strip()
    
    if user_id not in USER_SESSIONS:
        return
    
    session_data = USER_SESSIONS[user_id]
    
    if session_data.get('step') == 'waiting_for_code':
        client = session_data.get('client')
        phone = session_data.get('phone')
        account_num = session_data.get('account_num')
        
        try:
            await client.sign_in(phone, code=message)
            me = await client.get_me()
            name = me.first_name or "មិនស្គាល់"
            
            await event.respond(
                f"✅ **បន្ថែមគណនីដោយជោគជ័យ!**\n\n"
                f"📱 គណនី: Ac{account_num}\n"
                f"👤 ឈ្មោះ: {name}\n"
                f"📞 លេខទូរស័ព្ទ: {phone}\n\n"
                f"ប្រើពាក្យបញ្ជា `/list_accounts` ដើម្បីមើលគណនីទាំងអស់។\n"
                f"ប្រើពាក្យបញ្ជា `/start` ម្ដងទៀតដើម្បីដំណើរការ bot។",
                parse_mode='md'
            )
            
            await client.disconnect()
            del USER_SESSIONS[user_id]
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "password" in error_msg or "2fa" in error_msg:
                USER_SESSIONS[user_id]['step'] = 'waiting_for_password'
                USER_SESSIONS[user_id]['temp_code'] = message
                
                await event.respond(
                    "🔐 **បានរកឃើញ 2FA**\n\n"
                    "សូមបញ្ចូលពាក្យសម្ងាត់គណនីរបស់អ្នក៖",
                    parse_mode='md'
                )
            else:
                await event.respond(f"❌ កំហុស: {str(e)}")
                if client:
                    await client.disconnect()
                del USER_SESSIONS[user_id]
    
    elif session_data.get('step') == 'waiting_for_password':
        client = session_data.get('client')
        password = message
        account_num = session_data.get('account_num')
        phone = session_data.get('phone')
        
        try:
            await client.sign_in(password=password)
            me = await client.get_me()
            name = me.first_name or "មិនស្គាល់"
            
            await event.respond(
                f"✅ **បន្ថែមគណនីដោយជោគជ័យ!**\n\n"
                f"📱 គណនី: Ac{account_num}\n"
                f"👤 ឈ្មោះ: {name}\n"
                f"📞 លេខទូរស័ព្ទ: {phone}\n\n"
                f"ប្រើពាក្យបញ្ជា `/list_accounts` ដើម្បីមើលគណនីទាំងអស់។",
                parse_mode='md'
            )
            
            await client.disconnect()
            del USER_SESSIONS[user_id]
            
        except Exception as e:
            await event.respond(f"❌ កំហុស: {str(e)}")
            if client:
                await client.disconnect()
            del USER_SESSIONS[user_id]

# ==================== ចាប់ផ្តើមដំណើរការរាយការណ៍ ====================
async def start_reporting(event):
    user_id = event.sender_id
    user_data = USER_DATA.get(user_id, {})
    
    target = user_data.get('target')
    reason = user_data.get('reason')
    reason_display = user_data.get('reason_display')
    count = user_data.get('count')
    
    if not all([target, reason, count]):
        await event.edit("❌ ព័ត៌មានមិនពេញលេញ។ សូមចាប់ផ្តើមឡើងវិញជាមួយ /start")
        return
    
    session_files = [f for f in listdir('sessions') if f.endswith('.session')]
    
    if not session_files:
        await event.edit("❌ រកមិនឃើញគណនី! ប្រើ /add_account ដើម្បីបន្ថែមគណនី។")
        return
    
    total_reports = len(session_files) * count
    estimated_time = total_reports * 0.5
    
    hours = int(estimated_time // 3600)
    minutes = int((estimated_time % 3600) // 60)
    seconds = int(estimated_time % 60)
    
    time_text = ""
    if hours > 0:
        time_text += f"{hours} ម៉ោង "
    if minutes > 0:
        time_text += f"{minutes} នាទី "
    time_text += f"{seconds} វិនាទី"
    
    await event.edit(
        f"🔄 **កំពុងចាប់ផ្តើមរាយការណ៍...**\n\n"
        f"📢 ឆានែលគោលដៅ: @{target}\n"
        f"📋 មូលហេតុ: {reason_display}\n"
        f"🔢 ចំនួនដងក្នុងមួយគណនី: {count:,}\n"
        f"👥 ចំនួនគណនីដែលមាន: {len(session_files)}\n"
        f"📊 សរុបទាំងអស់: {total_reports:,} ដង\n"
        f"⏱ ពេលប៉ាន់ស្មាន: {time_text}\n\n"
        f"⏳ សូមរង់ចាំបន្តិច...\n"
        f"⚠️ ខ្ញុំនឹងជូនដំណឹងអ្នកពេលរួចរាល់។",
        parse_mode='md'
    )
    
    progress_msg = await event.respond("📊 វឌ្ឍនភាព: 0%", parse_mode='md')
    
    results = await run_reports(target, reason, count, session_files, progress_msg)
    
    success = results['success']
    failed = results['failed']
    details = results['details']
    total_time = results.get('total_time', 0)
    
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)
    
    time_text = ""
    if hours > 0:
        time_text += f"{hours} ម៉ោង "
    if minutes > 0:
        time_text += f"{minutes} នាទី "
    time_text += f"{seconds} វិនាទី"
    
    result_message = (
        f"**✅ រាយការណ៍រួចរាល់!**\n\n"
        f"📊 **ស្ថិតិ:**\n"
        f"✅ ជោគជ័យ: {success:,}\n"
        f"❌ បរាជ័យ: {failed:,}\n"
        f"📝 សរុប: {success + failed:,} ដង\n"
        f"⏱ ពេលសរុប: {time_text}\n\n"
        f"**សកម្មភាពថ្មីៗ:**\n"
    )
    
    for detail in details[-8:]:
        result_message += f"{detail}\n"
    
    buttons = [
        [Button.inline("🔄 រាយការណ៍ថ្មី", b'reporter')],
        [Button.url("📞 ទំនាក់ទំនងអ្នកអភិវឌ្ឍ", "https://t.me/mengheang25")]
    ]
    
    await event.respond(result_message, buttons=buttons, parse_mode='md')
    
    if user_id in USER_STATES:
        del USER_STATES[user_id]
    if user_id in USER_DATA:
        del USER_DATA[user_id]

# ==================== អនុវត្តការរាយការណ៍ ====================
async def run_reports(target, reason, count_per_account, session_files, progress_msg=None):
    results = {
        'success': 0,
        'failed': 0,
        'details': [],
        'total_time': 0
    }
    
    start_time = time.time()
    total_accounts = len(session_files)
    total_reports = total_accounts * count_per_account
    reports_done = 0
    
    reason_class = REASON_CLASSES.get(reason, InputReportReasonSpam())
    
    for account_idx, session_file in enumerate(session_files, 1):
        client = None
        try:
            account_num = search(r'Ac(\d+)\.session', session_file)
            account_num = account_num.group(1) if account_num else str(account_idx)
            
            session_name = session_file.replace('.session', '')
            client = TelegramClient(f'sessions/{session_name}', API_ID, API_HASH)
            await client.connect()
            
            if not await client.is_user_authorized():
                results['details'].append(f"❌ គណនី Ac{account_num}: មិនទាន់អនុញ្ញាត")
                results['failed'] += count_per_account
                reports_done += count_per_account
                await client.disconnect()
                continue
            
            me = await client.get_me()
            name = me.first_name or f"អ្នកប្រើ{account_num}"
            
            try:
                entity = await client.get_entity(target)
            except Exception as e:
                results['details'].append(f"❌ គណនី {name}: រកមិនឃើញឆានែល {target}")
                results['failed'] += count_per_account
                reports_done += count_per_account
                await client.disconnect()
                continue
            
            try:
                await client(JoinChannelRequest(entity))
                await asyncio.sleep(2)
            except Exception as e:
                results['details'].append(f"⚠️ {name}: {str(e)[:50]}")
            
            account_success = 0
            account_failed = 0
            
            for i in range(count_per_account):
                try:
                    result = await client(ReportPeerRequest(
                        peer=entity,
                        reason=reason_class,
                        message=f"រាយការណ៍សម្រាប់ {reason}"
                    ))
                    
                    if result:
                        account_success += 1
                        results['success'] += 1
                    else:
                        account_failed += 1
                        results['failed'] += 1
                    
                    reports_done += 1
                    
                    if (i + 1) % 10 == 0 or (i + 1) == count_per_account:
                        progress = int((reports_done / total_reports) * 100)
                        if progress_msg:
                            try:
                                percentage = min(progress, 100)
                                await progress_msg.edit(
                                    f"📊 វឌ្ឍនភាព: {percentage}% | {name}: {i+1:,}/{count_per_account:,}"
                                )
                            except:
                                pass
                    
                    await asyncio.sleep(0.5)
                    
                except FloodWaitError as e:
                    wait_time = e.seconds
                    results['details'].append(f"⚠️ {name}: ត្រូវរង់ចាំ {wait_time} វិនាទី")
                    await asyncio.sleep(wait_time)
                    account_failed += 1
                    results['failed'] += 1
                    reports_done += 1
                    
                except Exception as e:
                    account_failed += 1
                    results['failed'] += 1
                    reports_done += 1
                    
                    if "FLOOD_WAIT" in str(e):
                        import re
                        wait = re.search(r'(\d+)', str(e))
                        if wait:
                            await asyncio.sleep(int(wait.group(1)))
            
            emoji = "✅" if account_success > account_failed else "⚠️" if account_success > 0 else "❌"
            results['details'].append(
                f"{emoji} {name}: {account_success:,} ជោគជ័យ, {account_failed:,} បរាជ័យ"
            )
            await client.disconnect()
            
        except Exception as e:
            results['details'].append(f"❌ កំហុសគណនី: {str(e)[:50]}")
            results['failed'] += count_per_account
            reports_done += count_per_account
        finally:
            if client and client.is_connected():
                await client.disconnect()
    
    results['total_time'] = time.time() - start_time
    
    if progress_msg:
        try:
            await progress_msg.edit(
                f"📊 វឌ្ឍនភាព: 100% - រួចរាល់! ({results['total_time']:.1f}វិ)"
            )
        except:
            pass
    
    return results

# ==================== ពាក្យបញ្ជា /add_account ====================
@bot.on(events.NewMessage(pattern='/add_account'))
async def add_account_handler(event):
    user_id = event.sender_id
    
    if user_id != OWNER_ID:
        await event.respond("❌ អ្នកគ្មានសិទ្ធិបន្ថែមគណនីទេ។")
        return
    
    parts = event.message.text.split()
    if len(parts) != 2:
        await event.respond(
            "❌ **ទម្រង់មិនត្រឹមត្រូវ!**\n\n"
            "របៀបប្រើ: `/add_account +1234567890`\n\n"
            "ឧទាហរណ៍: `/add_account +85512345678`",
            parse_mode='md'
        )
        return
    
    phone = parts[1]
    
    if not phone.startswith('+'):
        await event.respond("❌ លេខទូរស័ព្ទត្រូវចាប់ផ្តើមជាមួយ '+'")
        return
    
    if user_id in USER_SESSIONS:
        await event.respond("❌ អ្នកកំពុងបន្ថែមគណនីរួចហើយ។ សូមបញ្ចប់ជាមុនសិន។")
        return
    
    session_files = [f for f in listdir('sessions') if f.endswith('.session')]
    
    numbers = []
    for f in session_files:
        match = search(r'Ac(\d+)\.session', f)
        if match:
            numbers.append(int(match.group(1)))
    
    next_num = max(numbers) + 1 if numbers else 1
    
    session_name = f'sessions/Ac{next_num}'
    
    USER_SESSIONS[user_id] = {
        'phone': phone,
        'step': 'waiting_for_code',
        'account_num': next_num
    }
    
    client = TelegramClient(session_name, API_ID, API_HASH)
    USER_SESSIONS[user_id]['client'] = client
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            
            await event.respond(
                f"📱 **ផ្ញើលេខកូដផ្ទៀងផ្ទាត់រួចរាល់!**\n\n"
                f"📞 លេខទូរស័ព្ទ: `{phone}`\n"
                f"📱 គណនី: Ac{next_num}\n\n"
                "សូមបញ្ចូលលេខកូដផ្ទៀងផ្ទាត់ (6 ខ្ទង់)៖",
                parse_mode='md'
            )
        else:
            await event.respond(f"✅ គណនី Ac{next_num} បានអនុញ្ញាតរួចហើយ!")
            await client.disconnect()
            del USER_SESSIONS[user_id]
            
    except PhoneNumberInvalidError:
        await event.respond("❌ លេខទូរស័ព្ទមិនត្រឹមត្រូវ!")
        await client.disconnect()
        del USER_SESSIONS[user_id]
    except Exception as e:
        await event.respond(f"❌ កំហុស: {str(e)}")
        await client.disconnect()
        del USER_SESSIONS[user_id]

# ==================== ពាក្យបញ្ជា /list_accounts ====================
@bot.on(events.NewMessage(pattern='/list_accounts'))
async def list_accounts_handler(event):
    user_id = event.sender_id
    
    if user_id != OWNER_ID:
        await event.respond("❌ អ្នកគ្មានសិទ្ធិមើលបញ្ជីគណនីទេ។")
        return
    
    session_files = [f for f in listdir('sessions') if f.endswith('.session')]
    
    if not session_files:
        await event.respond("❌ រកមិនឃើញគណនី។ ប្រើ `/add_account` ដើម្បីបន្ថែម។", parse_mode='md')
        return
    
    message = "**📱 បញ្ជីគណនីរបស់អ្នក:**\n\n"
    
    for session in sorted(session_files):
        try:
            client = TelegramClient(f'sessions/{session.replace(".session", "")}', API_ID, API_HASH)
            await client.connect()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                name = me.first_name or "មិនស្គាល់"
                phone = me.phone or "មិនស្គាល់"
                status = "✅ សកម្ម"
            else:
                name = "មិនទាន់អនុញ្ញាត"
                phone = "មិនស្គាល់"
                status = "❌ មិនទាន់អនុញ្ញាត"
            
            await client.disconnect()
            message += f"• `{session}` - 👤 {name} - 📞 +{phone} - {status}\n"
            
        except Exception as e:
            message += f"• `{session}` - ❌ កំហុស: {str(e)[:30]}\n"
    
    message += f"\nសរុប: {len(session_files)} គណនី"
    
    await event.respond(message, parse_mode='md')

# ==================== ពាក្យបញ្ជា /remove_account ====================
@bot.on(events.NewMessage(pattern='/remove_account'))
async def remove_account_handler(event):
    user_id = event.sender_id
    
    if user_id != OWNER_ID:
        await event.respond("❌ អ្នកគ្មានសិទ្ធិលុបគណនីទេ។")
        return
    
    parts = event.message.text.split()
    if len(parts) != 2:
        await event.respond(
            "❌ **ទម្រង់មិនត្រឹមត្រូវ!**\n\n"
            "របៀបប្រើ: `/remove_account Ac1`\n\n"
            "ប្រើ `/list_accounts` ដើម្បីមើលឈ្មោះគណនី។",
            parse_mode='md'
        )
        return
    
    account_name = parts[1]
    if not account_name.endswith('.session'):
        account_name += '.session'
    
    file_path = f'sessions/{account_name}'
    
    try:
        if path.exists(file_path):
            remove(file_path)
            await event.respond(f"✅ លុបគណនី {account_name} ដោយជោគជ័យ!")
        else:
            await event.respond(f"❌ រកមិនឃើញគណនី {account_name}!")
    except Exception as e:
        await event.respond(f"❌ កំហុស: {str(e)}")

# ==================== ពាក្យបញ្ជា /help ====================
@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    help_text = """
**🤖 ជំនួយអំពី Telegram Report Bot**

**ពាក្យបញ្ជា៖**
• `/start` - ចាប់ផ្តើមប្រើប្រាស់ bot
• `/help` - បង្ហាញសារជំនួយនេះ
• `/add_account +85512345678` - បន្ថែមគណនីថ្មី
• `/list_accounts` - បង្ហាញបញ្ជីគណនីទាំងអស់
• `/remove_account Ac1` - លុបគណនី
• `/stats` - បង្ហាញស្ថិតិរបស់ bot
• `/clear_sessions` - សម្អាត session ដែលមិនដំណើរការ

**របៀបរាយការណ៍៖**
1. ចុចប៊ូតុង **"📢 Reporter"**
2. បញ្ចូលឈ្មោះឆានែលគោលដៅ
3. ជ្រើសរើសមូលហេតុ
4. បញ្ចូលចំនួនដង (ប៉ុន្មានក៏បាន)
5. ចុច **"🚀 ចាប់ផ្តើមរាយការណ៍"**

**មូលហេតុនៃការរាយការណ៍៖**
• spam - សារឥតបានការ
• fake_account - គណនីក្លែងក្លាយ
• violence - អំពើហិង្សា
• child_abuse - រំលោភបំពានកុមារ
• pornography - រូបភាពអាសអាភាស
• geoirrelevant - មិនពាក់ព័ន្ធនឹងភូមិសាស្ត្រ

**អ្នកអភិវឌ្ឍន៍:** @mengheang25
"""
    await event.respond(help_text, parse_mode='md')

# ==================== ពាក្យបញ្ជា /stats ====================
@bot.on(events.NewMessage(pattern='/stats'))
async def stats_handler(event):
    user_id = event.sender_id
    
    if user_id != OWNER_ID:
        await event.respond("❌ អ្នកគ្មានសិទ្ធិមើលស្ថិតិទេ។")
        return
    
    session_files = [f for f in listdir('sessions') if f.endswith('.session')]
    
    authorized = 0
    for session in session_files:
        try:
            client = TelegramClient(f'sessions/{session.replace(".session", "")}', API_ID, API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                authorized += 1
            await client.disconnect()
        except:
            pass
    
    stats_text = (
        f"**📊 ស្ថិតិរបស់ Bot**\n\n"
        f"📁 ចំនួន session សរុប: {len(session_files)}\n"
        f"✅ បានអនុញ្ញាត: {authorized}\n"
        f"❌ មិនទាន់អនុញ្ញាត: {len(session_files) - authorized}\n"
        f"👥 អ្នកប្រើប្រាស់សកម្ម: {len(USER_STATES)}\n"
        f"📝 កំពុងបន្ថែមគណនី: {len(USER_SESSIONS)}\n"
    )
    
    await event.respond(stats_text, parse_mode='md')

# ==================== ពាក្យបញ្ជា /clear_sessions ====================
@bot.on(events.NewMessage(pattern='/clear_sessions'))
async def clear_sessions_handler(event):
    user_id = event.sender_id
    
    if user_id != OWNER_ID:
        await event.respond("❌ អ្នកគ្មានសិទ្ធិប្រើពាក្យបញ្ជានេះទេ។")
        return
    
    session_files = [f for f in listdir('sessions') if f.endswith('.session')]
    removed = 0
    
    for session in session_files:
        try:
            client = TelegramClient(f'sessions/{session.replace(".session", "")}', API_ID, API_HASH)
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                remove(f'sessions/{session}')
                removed += 1
            else:
                await client.disconnect()
        except:
            try:
                remove(f'sessions/{session}')
                removed += 1
            except:
                pass
    
    await event.respond(f"✅ បានសម្អាត {removed} session ដែលមិនដំណើរការ។")

# ==================== មុខងារសម្អាត ====================
async def cleanup():
    global bot
    if bot and bot.is_connected():
        print("🔄 កំពុងផ្តាច់ bot...")
        await bot.disconnect()
        print("✅ បានផ្តាច់ bot ដោយជោគជ័យ")

# ==================== មុខងារចម្បង ====================
async def main():
    global bot
    
    print("=" * 50)
    print("🤖 Telegram Report Bot កំពុងចាប់ផ្តើម...")
    print("=" * 50)
    print(f"📱 Owner ID: {OWNER_ID}")
    print(f"🔑 API ID: {API_ID}")
    print("=" * 50)
    print("✅ Bot កំពុងដំណើរការ! ចុច Ctrl+C ដើម្បីបញ្ឈប់។")
    print("=" * 50)
    
    await bot.start(bot_token=BOT_TOKEN)
    
    try:
        await bot.run_until_disconnected()
    except asyncio.CancelledError:
        print("🔄 Bot task cancelled...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await cleanup()

# ==================== ចំណុចចាប់ផ្តើម ====================
if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n👋 បានបញ្ឈប់ bot ដោយអ្នកប្រើប្រាស់")
    except Exception as e:
        print(f"❌ កំហុស: {e}")
    finally:
        try:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        except:
            pass
        print("👋 លាហើយ!")