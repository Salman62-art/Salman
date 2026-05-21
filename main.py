import discord
from discord.ext import commands
from discord import ui, app_commands
import os
from flask import Flask
from threading import Thread

# كود لمنع إيقاف البوت في الموقع
app = Flask('')
@app.route('/')
def home():
    return "✅ البوت يعمل بنجاح!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- الإعدادات الأساسية ----------------
TOKEN = os.environ.get('TOKEN')
STAFF_CHANNEL_ID = 123456789  # آيدي روم الإدارة
ADMIN_ROLE_ID = 987654321    # آيدي رتبة الإدارة العليا

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # تسجيل الأزرار للعمل بشكل مستمر
        self.add_view(SingleButtonView("تقديم إدارة 👔", discord.ButtonStyle.success, "btn_admin"))
        self.add_view(SingleButtonView("تقديم هوست 🎙️", discord.ButtonStyle.primary, "btn_host"))
        self.add_view(SingleButtonView("تقديم مباحث 👮‍♂️", discord.ButtonStyle.danger, "btn_police"))
        self.add_view(SingleButtonView("تقديم مصور 🎥", discord.ButtonStyle.secondary, "btn_cam"))
        self.add_view(SingleButtonView("تقديم عسكرية 🎖️", discord.ButtonStyle.success, "btn_military"))
        self.add_view(SingleButtonView("تقديم إعلام 📢", discord.ButtonStyle.primary, "btn_media"))
        
        await self.tree.sync()
        print(f"✅ تم تحميل الأوامر بنجاح!")

# تشغيل نظام الحماية
keep_alive()
bot = MyBot()

# --- نافذة الأسئلة ---
class ApplyModal(ui.Modal):
    def __init__(self, title, questions_list):
        super().__init__(title=title)
        self.inputs = []
        for q in questions_list:
            t_input = ui.TextInput(label=q, style=discord.TextStyle.paragraph, required=True)
            self.add_item(t_input)
            self.inputs.append(t_input)

    async def on_submit(self, interaction: discord.Interaction):
        staff_channel = bot.get_channel(STAFF_CHANNEL_ID)
        embed = discord.Embed(title=f"📋 تقديم جديد: {self.title}", color=discord.Color.green())
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.add_field(name="👤 المقدم:", value=interaction.user.mention, inline=False)
        for i in self.inputs:
            embed.add_field(name=i.label, value=i.value, inline=False)
        
        await staff_channel.send(content=f"🔔 <@&{ADMIN_ROLE_ID}> | تقديم جديد!", embed=embed)
        await interaction.response.send_message("✅ تم إرسال تقديمك بنجاح!", ephemeral=True)

# --- نظام الأزرار ---
class SingleButtonView(ui.View):
    def __init__(self, label, style, custom_id, questions=None):
        super().__init__(timeout=None)
        self.default_questions = ["الاسم الثلاثي والعمر", "خبرتك في هذا القسم", "لماذا تستحق المنصب؟"]
        self.questions = questions or self.default_questions
        btn = ui.Button(label=label, style=style, custom_id=custom_id)
        btn.callback = self.btn_callback
        self.add_item(btn)

    async def btn_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ApplyModal(interaction.component.label, self.questions))

def parse_questions(q_str):
    if not q_str: return None
    sep = '،' if '،' in q_str else ','
    return [q.strip() for q in q_str.split(sep)][:5]

# --- الأوامر ---
@bot.tree.command(name="setup_admin", description="إرسال زر تقديم الإدارة")
@app_commands.describe(questions="اختياري: اكتب الأسئلة وافصل بينها بفاصلة")
async def setup_admin(interaction: discord.Interaction, questions: str = None):
    view = SingleButtonView("تقديم إدارة 👔", discord.ButtonStyle.success, "btn_admin", parse_questions(questions))
    await interaction.response.send_message("📋 للتقديم على الإدارة:", view=view)

@bot.tree.command(name="setup_host", description="إرسال زر تقديم الهوست")
@app_commands.describe(questions="اختياري: اكتب الأسئلة وافصل بينها بفاصلة")
async def setup_host(interaction: discord.Interaction, questions: str = None):
    view = SingleButtonView("تقديم هوست 🎙️", discord.ButtonStyle.primary, "btn_host", parse_questions(questions))
    await interaction.response.send_message("🎤 للتقديم على الهوست:", view=view)

@bot.tree.command(name="setup_police", description="إرسال زر تقديم المباحث")
@app_commands.describe(questions="اختياري: اكتب الأسئلة وافصل بينها بفاصلة")
async def setup_police(interaction: discord.Interaction, questions: str = None):
    view = SingleButtonView("تقديم مباحث 👮‍♂️", discord.ButtonStyle.danger, "btn_police", parse_questions(questions))
    await interaction.response.send_message("🕵️ للتقديم على المباحث:", view=view)

@bot.tree.command(name="setup_cam", description="إرسال زر تقديم المصور")
@app_commands.describe(questions="اختياري: اكتب الأسئلة وافصل بينها بفاصلة")
async def setup_cam(interaction: discord.Interaction, questions: str = None):
    view = SingleButtonView("تقديم مصور 🎥", discord.ButtonStyle.secondary, "btn_cam", parse_questions(questions))
    await interaction.response.send_message("📸 للتقديم على المصور:", view=view)

@bot.tree.command(name="setup_military", description="إرسال زر تقديم العسكرية")
@app_commands.describe(questions="اختياري: اكتب الأسئلة وافصل بينها بفاصلة")
async def setup_military(interaction: discord.Interaction, questions: str = None):
    view = SingleButtonView("تقديم عسكرية 🎖️", discord.ButtonStyle.success, "btn_military", parse_questions(questions))
    await interaction.response.send_message("🎖️ للتقديم على العسكرية:", view=view)

@bot.tree.command(name="setup_media", description="إرسال زر تقديم الإعلام")
@app_commands.describe(questions="اختياري: اكتب الأسئلة وافصل بينها بفاصلة")
async def setup_media(interaction: discord.Interaction, questions: str = None):
    view = SingleButtonView("تقديم إعلام 📢", discord.ButtonStyle.primary, "btn_media", parse_questions(questions))
    await interaction.response.send_message("📢 للتقديم على الإعلام:", view=view)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل وجاهز!')

bot.run(TOKEN)
                 
