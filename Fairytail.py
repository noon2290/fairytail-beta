import discord
from discord import app_commands
from discord.ext import commands
import discord
from discord.ext import commands
import json
import os
from myserver import server_on

bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())



@bot.event
async def on_ready():
    print("Bot Online!")
    synced = await bot.tree.sync()
    print(f"{len(synced)} command(s)")


# แจ้งคนเข้า - ออกเซิร์ฟ
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1377573485110624309) # ID ห้อง
    text = f"# Welcome to the Fairytail, {member.mention}!"

    emmbed = discord.Embed(title = 'ยินดีต้อนรับสู่กิลด์แฟรี่เทล!',
                           description = 'เดินทางมาเหนื่อย ๆ เลยใช่มั้ย? ไปทำภารกิจกันเถอะ!',
                           color = 0xFF8B13,
                           timestamp=discord.utils.utcnow())
    emmbed.set_author(name='Fairytail', icon_url='https://iili.io/3Dd5XTB.png')
    emmbed.set_image(url='https://iili.io/3pbLK7I.png')  # รูปใหญ่อยู่ล่าง

    await channel.send(text) #ส่งข้อความไปช่องนี้
    await channel.send(embed = emmbed)

# คำสั่งแชทบอท
@bot.event
async def on_message(message):
    mes = message.content # ดึงข้อความที่ถูกส่งมา
    if mes == 'สวัสดี':
        await message.channel.send("สวัสดีจอมเวทย์") # ข้อความที่ส่งกลับ

    elif mes == 'สวัสดีแฟรี่เทล':
        await message.channel.send("สวัสดี! ยินดีต้อนรับ " + str(message.author.name)) # ข้อความที่ส่งกลับ

    await bot.process_commands(message)
    # ทำคำสั่ง event แล้วไปทำคำสั่ง bot command ต่อ

# กำหนดคำสั่งให้บอท
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx. author.name}")

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


# ข้อมูลผู้เล่น
player_data = {}

# ระดับกิลด์และแต้มที่ต้องการ
guild_levels = {
    1: 0,
    2: 100,
    3: 250,
    4: 500,
    5: 1000,
}

guild_level_names = {
    1: "Basic",
    2: "C-Class",
    3: "B-Class",
    4: "A-Class",
    5: "S-Class",
}

# ID ของผู้ดูแล (เปลี่ยนเป็น ID ของคุณ)
ADMIN_IDS = [467945022264705027]

# ฟังก์ชันโหลดและบันทึกข้อมูล
def load_data():
    global player_data
    if os.path.exists('.venv/player_data.json'):
        with open('.venv/player_data.json', 'r', encoding='utf-8') as f:
            player_data = json.load(f)


def save_data():
    with open('.venv/player_data.json', 'w', encoding='utf-8') as f:
        json.dump(player_data, f, ensure_ascii=False, indent=2)


def init_player(user_id):
    """สร้างข้อมูลผู้เล่นใหม่"""
    if str(user_id) not in player_data:
        player_data[str(user_id)] = {
            'jewels': 0,
            'guild_exp': 0,
            'guild_level': 1
        }
        save_data()


def get_guild_level(exp):
    """คำนวณระดับกิลด์จากแต้ม"""
    for level in sorted(guild_levels.keys(), reverse=True):
        if exp >= guild_levels[level]:
            return level
    return 1


def is_admin(user_id):
    """ตรวจสอบว่าเป็นผู้ดูแลหรือไม่"""
    return user_id in ADMIN_IDS


# Event เมื่อ Bot พร้อมใช้งาน
@bot.event
async def on_ready():
    print(f'{bot.user} ได้เข้าสู่ระบบแล้ว!')
    load_data()


# =================
# คำสั่งระบบเงินตรา
# =================

@bot.command(name='jewel')
async def check_jewel(ctx, member: discord.Member = None):
    """เช็คจำนวน Jewel ของตัวเองหรือคนอื่น"""
    target = member or ctx.author
    init_player(target.id)

    jewels = player_data[str(target.id)]['jewels']

    embed = discord.Embed(
        title=f"ยอดเงินของ {target.display_name}",
        description=f"Total {jewels:,} 💎",
        color=0x00ff00,
        timestamp=discord.utils.utcnow()
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_author(name='Fairytail',icon_url='https://iili.io/3ydS6fj.png')
    await ctx.send(embed=embed)


@bot.command(name='givejewel')
async def give_jewel(ctx, member: discord.Member, amount: int):
    """[ผู้ดูแลเท่านั้น] สร้าง Jewel ให้ผู้เล่น"""
    if not any(role.name == "Master" for role in ctx.author.roles):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้!")
        return

    if amount <= 0:
        await ctx.send("❌ จำนวน Jewel ต้องมากกว่า 0!")
        return

    init_player(member.id)
    player_data[str(member.id)]['jewels'] += amount
    save_data()

    embed = discord.Embed(
        title="💎 Jewel Created!",
        description=f"ส่ง **{amount:,}** Jewels ให้ {member.display_name}",
        color=0x00ff00
    )

    await ctx.send(embed=embed)

@bot.command(name='removejewel')
async def remove_jewel(ctx, member: discord.Member, amount: int):
    """[ผู้ดูแลเท่านั้น] ลบ Jewel จากผู้เล่น"""
    if not any(role.name == "Master" for role in ctx.author.roles):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้!")
        return

    if amount <= 0:
        await ctx.send("❌ จำนวน Jewel ต้องมากกว่า 0!")
        return

    init_player(member.id)
    current = player_data[str(member.id)]['jewels']
    if current < amount:
        await ctx.send(f"❌ {member.display_name} มี Jewel ไม่เพียงพอ! (ปัจจุบัน: {current})")
        return

    player_data[str(member.id)]['jewels'] -= amount
    save_data()

    embed = discord.Embed(
        title="💎 Jewel Removed!",
        description=f"หัก **{amount:,}** Jewels จาก {member.display_name}",
        color=0xff0000,
        timestamp = discord.utils.utcnow()
    )
    embed.set_author(name='Fairytail', icon_url='https://iili.io/3ydS6fj.png')
    await ctx.send(embed=embed)


@bot.command(name='pay')
async def pay_jewel(ctx, member: discord.Member, amount: int):
    """โอน Jewel ให้ผู้เล่นคนอื่น"""
    if member == ctx.author:
        await ctx.send("❌ คุณไม่สามารถโอนเงินให้ตัวเองได้!")
        return

    if amount <= 0:
        await ctx.send("❌ จำนวน Jewel ต้องมากกว่า 0!")
        return

    init_player(ctx.author.id)
    init_player(member.id)

    sender_jewels = player_data[str(ctx.author.id)]['jewels']

    if sender_jewels < amount:
        await ctx.send(f"❌ คุณมี Jewel ไม่เพียงพอ! (มี {sender_jewels:,} Jewels)")
        return

    # โอนเงิน
    player_data[str(ctx.author.id)]['jewels'] -= amount
    player_data[str(member.id)]['jewels'] += amount
    save_data()

    embed = discord.Embed(
        title="💰 Payment Successful!",
        description=f"{ctx.author.display_name} ได้โอน **{amount:,}** Jewels ให้ {member.display_name}",
        color=0x00ff00,
        timestamp=discord.utils.utcnow()
    )
    embed.set_author(name='Fairytail', icon_url='https://iili.io/3ydS6fj.png')
    await ctx.send(embed=embed)


# ==================
# คำสั่งระบบกิลด์
# ==================

@bot.command(name='guildexp')
async def add_guild_exp(ctx, member: discord.Member, amount: int):
    """[ผู้ดูแลเท่านั้น] เพิ่มแต้มกิลด์ให้ผู้เล่น"""
    if not any(role.name == "Master" for role in ctx.author.roles):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้!")
        return

    if amount <= 0:
        await ctx.send("❌ จำนวนแต้มต้องมากกว่า 0!")
        return

    init_player(member.id)

    old_level = player_data[str(member.id)]['guild_level']
    player_data[str(member.id)]['guild_exp'] += amount
    new_level = get_guild_level(player_data[str(member.id)]['guild_exp'])
    player_data[str(member.id)]['guild_level'] = new_level

    save_data()

    embed = discord.Embed(
        title="⭐ Guild EXP Added!",
        description=f"เพิ่ม **{amount}** แต้มให้ {member.display_name}",
        color=0x0099ff,
        timestamp=discord.utils.utcnow()
    )
    embed.set_author(name='Fairytail', icon_url='https://iili.io/3ydS6fj.png')

    if new_level > old_level:
        embed.add_field(
            name="🎉 Level Up!",
            value=f"เลื่อนระดับจาก **{guild_level_names[old_level]}** เป็น **{guild_level_names[new_level]}**",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='removeguildexp')
async def remove_guild_exp(ctx, member: discord.Member, amount: int):
    """[ผู้ดูแลเท่านั้น] ลบแต้มกิลด์จากผู้เล่น"""
    if not any(role.name == "Master" for role in ctx.author.roles):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้!")
        return

    if amount <= 0:
        await ctx.send("❌ จำนวนแต้มต้องมากกว่า 0!")
        return

    init_player(member.id)

    current_exp = player_data[str(member.id)]['guild_exp']
    if current_exp < amount:
        await ctx.send(f"❌ {member.display_name} มีแต้มกิลด์ไม่เพียงพอ! (ปัจจุบัน: {current_exp})")
        return

    player_data[str(member.id)]['guild_exp'] -= amount
    new_level = get_guild_level(player_data[str(member.id)]['guild_exp'])
    old_level = player_data[str(member.id)]['guild_level']
    player_data[str(member.id)]['guild_level'] = new_level

    save_data()

    embed = discord.Embed(
        title="⭐ Guild EXP Removed!",
        description=f"ลบ **{amount}** แต้มจาก {member.display_name}",
        color=0xff9900,
        timestamp=discord.utils.utcnow()
    )
    embed.set_author(name='Fairytail', icon_url='https://iili.io/3ydS6fj.png')

    if new_level < old_level:
        embed.add_field(
            name="🔻 Level Down!",
            value=f"ลดระดับจาก **{guild_level_names[old_level]}** เป็น **{guild_level_names[new_level]}**",
            inline=False
        )

    await ctx.send(embed=embed)


@bot.command(name='profile')
async def player_profile(ctx, member: discord.Member = None):
    """เช็คข้อมูลผู้เล่น"""
    target = member or ctx.author
    init_player(target.id)

    data = player_data[str(target.id)]
    jewels = data['jewels']
    guild_exp = data['guild_exp']
    guild_level = data['guild_level']
    guild_name = guild_level_names[guild_level]

    # คำนวณแต้มที่ต้องการสำหรับระดับถัดไป
    next_level = guild_level + 1
    if next_level in guild_levels:
        needed_exp = guild_levels[next_level] - guild_exp
        next_level_name = guild_level_names[next_level]
        progress = f"ต้องการอีก **{needed_exp}** แต้มเพื่อเป็น **{next_level_name}**"
    else:
        progress = "**ระดับสูงสุดแล้ว!**"

    embed = discord.Embed(
        title=f"โปรไฟล์ของ {target.display_name}",
        color=0xff6b35,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Jewels 💎", value=f"▪️ {jewels:,}", inline=False)
    embed.add_field(name="Guild Level ⭐", value=f"▪️ {guild_level} - {guild_name}", inline=False)
    embed.add_field(name="Guild EXP 🎯", value=f"▪️ {guild_exp}", inline=False)
    embed.add_field(name="ความคืบหน้า 📈", value=progress, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_author(name='Fairytail', icon_url='https://iili.io/3ydS6fj.png')

    await ctx.send(embed=embed)


@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """ตารางคะแนนผู้เล่น"""
    if not player_data:
        await ctx.send("❌ ยังไม่มีข้อมูลผู้เล่น!")
        return

    # เรียงลำดับตาม Guild EXP
    sorted_players = sorted(
        player_data.items(),
        key=lambda x: x[1]['guild_exp'],
        reverse=True
    )

    embed = discord.Embed(
        title="🏆 Guild Leaderboard",
        color=0xffd700
    )

    for i, (user_id, data) in enumerate(sorted_players[:10]):
        try:
            user = ctx.guild.get_member(int(user_id))
            name = user.display_name if user else f"User {user_id}"
            level_name = guild_level_names[data['guild_level']]

            embed.add_field(
                name=f"{i + 1}. {name}",
                value=f"Level {data['guild_level']} - {level_name}\nEXP: {data['guild_exp']}",
                inline=False
            )
        except:
            continue

    embed.set_author(name='Fairytail', icon_url='https://iili.io/3ydS6fj.png')
    await ctx.send(embed=embed)


# คำสั่งช่วยเหลือ
@bot.command(name='help_rpg')
async def help_rpg(ctx):
    """คู่มือการใช้งาน"""
    embed = discord.Embed(
        title="🎮 คู่มือการใช้งาน",
        color=0x7289da
    )

    embed.add_field(
        name="💎 คำสั่งระบบเงินตรา",
        value="""
        `!jewel [@user]` - เช็ค Jewel
        `!pay @user จำนวน` - โอน Jewel
        `!givejewel @user จำนวน` - [Admin] สร้าง Jewel
        """,
        inline=False
    )

    embed.add_field(
        name="⭐ คำสั่งระบบกิลด์",
        value="""
        `!profile [@user]` - เช็คข้อมูลผู้เล่น
        `!guildexp @user จำนวน` - [Admin] เพิ่มแต้มกิลด์
        `!leaderboard` - ตารางคะแนน
        """,
        inline=False
    )

    embed.add_field(
        name="🏅 ระดับกิลด์",
        value="""
        Level 1 (0 EXP): Class Mage
        Level 2 (100 EXP): C-Class Mage
        Level 3 (250 EXP): B-Class Mage
        Level 4 (500 EXP): A-Class Mage
        Level 5 (1000 EXP): S-Class Mage
        """,
        inline=False
    )

    await ctx.send(embed=embed)

server_on()

bot.run(os.getenv('TOKEN'))