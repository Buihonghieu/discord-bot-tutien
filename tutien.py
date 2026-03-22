#1: Khởi tạo, Cấu Hình & Dữ Liệu
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import json
import random
import time
from typing import Literal
import math
import os
from dotenv import load_dotenv

# 1. Hàm hỗ trợ gợi ý danh sách Pet (Autocomplete)
async def pet_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    # Lấy danh sách tên pet từ PET_DATA và thêm tùy chọn "None"
    all_pets = list(PET_DATA.keys()) + ["None"]
    return [
        app_commands.Choice(name=pet, value=pet)
        for pet in all_pets if current.lower() in pet.lower()
    ][:25] # Discord giới hạn tối đa 25 gợi ý

# --- 1.1 Cấu hình Intents & Bot ---
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

ADMIN_IDS = [1480398699174695044] 
THIEN_DAO_ID = 1480398699174695044  # Đổi thành Discord ID duy nhất của Thiên Đạo
VN_TZ = timezone(timedelta(hours=7))
MAX_LINH_KHI_NGAY = 3000

# --- 1.2 Database Tĩnh ---

# Đạo hữu lưu ý: Cảnh giới Nguyên Anh nằm ở Index 3 trong danh sách này
RANKS = [
    {"name": "Luyện Khí", "min": 0, "max": 2000},       # idx 0
    {"name": "Trúc Cơ", "min": 2000, "max": 6000},     # idx 1
    {"name": "Kim Đan", "min": 6000, "max": 15000},    # idx 2
    {"name": "Nguyên Anh", "min": 15000, "max": 35000}, # idx 3 - Bước ngoặt khó!
    {"name": "Hóa Thần", "min": 35000, "max": 75000},
    {"name": "Luyện Hư", "min": 75000, "max": 150000},
    {"name": "Hợp Thể", "min": 150000, "max": 300000},
    {"name": "Đại Thừa", "min": 300000, "max": 700000},
    {"name": "Độ Kiếp", "min": 700000, "max": 1500000},
    {"name": "Tiên Nhân", "min": 1500000, "max": 5000000}
]

PET_DATA = {
    "BKS": {"icon": "🍰", "rate": 70, "bonus_exp": 1.1, "reduce_time": 0, "fail_rate": 0.40, "rarity": "Thường", "tier": 1},      
    "Linh Miêu": {"icon": "🐱", "rate": 60, "bonus_exp": 1.2, "reduce_time": 0, "fail_rate": 0.40, "rarity": "Thường", "tier": 2}, 
    "Thanh Loan": {"icon": "🐦", "rate": 3, "bonus_exp": 1.5, "reduce_time": 15, "fail_rate": 0.35, "rarity": "Tốt", "tier": 3}, 
    "Hắc Tề Lân": {"icon": "🦄", "rate": 3, "bonus_exp": 1.7, "reduce_time": 15, "fail_rate": 0.35, "rarity": "Tốt", "tier": 4}, 
    "Cửu Vĩ Hồ": {"icon": "🦊", "rate": 0.3, "bonus_exp": 2.0, "reduce_time": 15, "fail_rate": 0.30, "rarity": "Cực Hiếm", "tier": 5}   
}

BOSS_DATA = {
    "Hắc Thiết Đại Tinh": {"hp": 2000, "atk": 150, "def": 50, "reward_lt": (5, 15), "drop_rate": 0.3, "scale": 1.2, "min_tier": 1},
    "Thiên Niên Yêu Thụ": {"hp": 8000, "atk": 450, "def": 150, "reward_lt": (20, 50), "drop_rate": 0.4, "scale": 1.3, "min_tier": 2},
    "Thái Cổ Long Quy": {"hp": 25000, "atk": 1100, "def": 500, "reward_lt": (60, 150), "drop_rate": 0.5, "scale": 1.4, "min_tier": 4},
    "Lôi Đình Tạc Ma": {"hp": 75000, "atk": 2500, "def": 1200, "reward_lt": (150, 350), "drop_rate": 0.6, "scale": 1.5, "min_tier": 5},
    "Cửu Vĩ Thiên Hồ": {"hp": 200000, "atk": 5500, "def": 2800, "reward_lt": (500, 1200), "drop_rate": 0.7, "scale": 1.6, "min_tier": 6},
    "Hỗn Độn Ma Tổ": {"hp": 1000000, "atk": 12000, "def": 8000, "reward_lt": (2000, 5000), "drop_rate": 0.85, "scale": 1.8, "min_tier": 7}
}

BAI_QUAI = [
    "Rừng U Minh", "Động Linh Thạch", "Vực Thẳm Ma Giới", "Đỉnh Tuyết Sơn", 
    "Hồ Nguyệt Quang", "Đảo Hoang Sơ", "Thung Lũng Tử Thần", "Mê Cung Cổ Đại", 
    "Suối Nguồn Linh Lực", "Hỏa Diệm Sơn"
]

EQUIPMENT_DATA = {
    "mu": {
        "Cấp 1": {"name": "Mũ Vải Thô Sơ", "def": 5},
        "Cấp 2": {"name": "Mũ Da Yêu Thú", "def": 20},
        "Cấp 3": {"name": "Thanh Đồng Quán", "def": 50},
        "Cấp 4": {"name": "Huyền Thiết Linh Mạo", "def": 120},
        "Cấp 5": {"name": "Lưu Ly Ngọc Quán", "def": 300},
        "Cấp 6": {"name": "Thái Ất Chân Quang Mạo", "def": 700},
        # --- THẦN KHÍ (Cấp 7 - 10) ---
        "Cấp 7": {"name": "Phượng Hoàng Niết Bàn Quán", "def": 1500},
        "Cấp 8": {"name": "Cửu Thiên Huyền Vũ Quán", "def": 3500},
        "Cấp 9": {"name": "Thánh Long Khải Thiên Quán", "def": 8000},
        "Cấp 10": {"name": "Hỗn Độn Vô Thượng Thần Quán", "def": 20000}
    },
    "giap": {
        "Cấp 1": {"name": "Áo Vải Thô Sơ", "def": 10},
        "Cấp 2": {"name": "Lân Giáp Yêu Lang", "def": 40},
        "Cấp 3": {"name": "Hắc Thiết Trọng Giáp", "def": 100},
        "Cấp 4": {"name": "Bạch Ngân Linh Giáp", "def": 250},
        "Cấp 5": {"name": "Xích Diệm Bảo Giáp", "def": 600},
        "Cấp 6": {"name": "Huyền Vũ Minh Giáp", "def": 1500},
        # --- THẦN KHÍ (Cấp 7 - 10) ---
        "Cấp 7": {"name": "Thái Cổ Long Lân Giáp", "def": 3500},
        "Cấp 8": {"name": "Bất Diệt Kim Thân Bào", "def": 8000},
        "Cấp 9": {"name": "Cửu Tiêu Thánh Quang Khải", "def": 18000},
        "Cấp 10": {"name": "Vĩnh Hằng Thiên Đạo Chiến Giáp", "def": 45000}
    },
    "gang": {
        "Cấp 1": {"name": "Găng Tay Thô Sơ", "hp": 15},
        "Cấp 2": {"name": "Hộ Thủ Bì Hổ", "hp": 50},
        "Cấp 3": {"name": "Găng Tay Tinh Cang", "hp": 120},
        "Cấp 4": {"name": "Băng Tinh Hộ Thủ", "hp": 300},
        "Cấp 5": {"name": "U Minh Ma Thủ", "hp": 700},
        "Cấp 6": {"name": "Càn Khôn Hộ Thủ", "hp": 1800},
        # --- THẦN KHÍ (Cấp 7 - 10) ---
        "Cấp 7": {"name": "Thần Lực Phá Thiên Thủ", "hp": 4000},
        "Cấp 8": {"name": "Vạn Tượng Quy Nhất Thủ", "hp": 10000},
        "Cấp 9": {"name": "Thánh Ma Hỗn Độn Thủ", "hp": 25000},
        "Cấp 10": {"name": "Chưởng Khống Thái Sơ Thần Thủ", "hp": 60000}
    },
    "giay": {
        "Cấp 1": {"name": "Giày Vải Thô Sơ", "hp": 15},
        "Cấp 2": {"name": "Tật Phong Ngoa", "hp": 50},
        "Cấp 3": {"name": "Vân Tiêu Ngoa", "hp": 120},
        "Cấp 4": {"name": "Thanh Loan Túc", "hp": 300},
        "Cấp 5": {"name": "Ngự Phong Thần Túc", "hp": 700},
        "Cấp 6": {"name": "Thất Tinh Bộ Ngoa", "hp": 1800},
        # --- THẦN KHÍ (Cấp 7 - 10) ---
        "Cấp 7": {"name": "Thiên Hành Vô Ảnh Túc", "hp": 4000},
        "Cấp 8": {"name": "Lôi Đình Vạn Lý Ngoa", "hp": 10000},
        "Cấp 9": {"name": "Thời Không Chuyển Hoán Túc", "hp": 25000},
        "Cấp 10": {"name": "Đạp Tuyết Vô Ngân Thiên Thần Túc", "hp": 60000}
    },
    "vukhi": {
        "Cấp 1": {"name": "Kiếm Gỗ Thô Sơ", "atk": 10},
        "Cấp 2": {"name": "Bách Luyện Tinh Thiết Kiếm", "atk": 30},
        "Cấp 3": {"name": "Thanh Lam Linh Đao", "atk": 80},
        "Cấp 4": {"name": "Xích Huyết Ma Kiếm", "atk": 200},
        "Cấp 5": {"name": "Hàn Băng Thần Thương", "atk": 500},
        "Cấp 6": {"name": "Trảm Ma Thần Đao", "atk": 1200},
        # --- THẦN KHÍ (Cấp 7 - 10) ---
        "Cấp 7": {"name": "Long Thần Phá Thiên Kích", "atk": 3000},
        "Cấp 8": {"name": "诛 Tiên Kiếm (Bản Thể)", "atk": 7500},
        "Cấp 9": {"name": "Thánh Quang Phán Quyết Kiếm", "atk": 18000},
        "Cấp 10": {"name": "Khai Thiên Tích Địa Thần Rìu", "atk": 40000}
    }
}

# --- 1.3 Hàm hỗ trợ gợi ý danh sách Boss (Autocomplete) ---
async def boss_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=boss, value=boss)
        for boss in BOSS_DATA.keys() if current.lower() in boss.lower()
    ][:25]

# --- 1.4 View xác nhận tổ đội ---
class BossConfirmView(discord.ui.View):
    def __init__(self, leader, team, boss_name, timeout=60):
        super().__init__(timeout=timeout)
        self.leader = leader
        self.team = team
        self.boss_name = boss_name
        self.ready_users = {leader.id}
        self.is_started = False

    @discord.ui.button(label="Sẵn Sàng ✅", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [m.id for m in self.team]:
            return await interaction.response.send_message("❌ Ngươi không có tên trong tổ đội!", ephemeral=True)
        
        self.ready_users.add(interaction.user.id)
        
        if len(self.ready_users) >= len(self.team):
            self.is_started = True
            await interaction.response.edit_message(content=f"⚔️ **Tất cả đã chuẩn bị!** Bắt đầu thảo phạt **{self.boss_name}**...", view=None)
            self.stop()
        else:
            remaining = len(self.team) - len(self.ready_users)
            await interaction.response.edit_message(content=f"⏳ Chờ đồng đội xác nhận... (Còn thiếu {remaining} người)")

    @discord.ui.button(label="Hủy ❌", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.leader.id:
            return await interaction.response.send_message("❌ Chỉ Trưởng nhóm mới có quyền hủy!", ephemeral=True)
        await interaction.response.edit_message(content="🚫 Chuyến chinh phạt đã bị Trưởng nhóm hủy bỏ.", view=None)
        self.stop()

# --- 1.5 Hàm hỗ trợ gợi ý danh sách Trang Bị (Autocomplete) ---

async def equipment_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    # Lấy giá trị của tham số 'loai' mà người dùng đang chọn
    loai_selected = interaction.namespace.loai 
    
    choices = []
    
    # Nếu đã chọn loại (mu, giap, vukhi...), chỉ lấy đồ trong loại đó
    if loai_selected in EQUIPMENT_DATA:
        category_data = EQUIPMENT_DATA[loai_selected]
        for level_info in category_data.values():
            item_name = level_info["name"]
            if current.lower() in item_name.lower():
                choices.append(app_commands.Choice(name=item_name, value=item_name))
    
    # Nếu chưa chọn loại hoặc đang gõ dở, có thể để trống hoặc hiện thông báo
    if not choices and not loai_selected:
        choices.append(app_commands.Choice(name="⚠️ Hãy chọn Loại trang bị trước", value="None"))

    return choices[:25]

# --- 1.6 Admin Command ---

@bot.tree.command(name="set_tuvi", description="[Thiên Đạo] Chỉnh sửa tu vi của một người chơi")
@app_commands.describe(user="Tu sĩ cần chỉnh", amount="Lượng tu vi mới")
async def set_tuvi(interaction: discord.Interaction, user: discord.Member, amount: int):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("❌ Ngươi không phải Thiên Đạo, không thể can thiệp nhân quả!", ephemeral=True)
    
    uid = str(user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Tu sĩ này chưa nhập đạo.", ephemeral=True)
    
    old_tuvi = data[uid]["tuvi"]
    data[uid]["tuvi"] = max(0, amount)
    save_data(data)
    
    await interaction.response.send_message(f"✨ **Thiên Đạo** đã thay đổi tu vi của **{user.display_name}**: `{old_tuvi}` -> `{amount}`")

@bot.tree.command(name="reset_tuvi", description="[Thiên Đạo] Đưa tu vi của một người về 0 (Vẫn giữ trang bị)")
async def reset_tuvi(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("❌ Ngươi không đủ pháp lực để thực hiện việc này!", ephemeral=True)
    
    uid = str(user.id)
    data = load_data()
    
    if uid in data:
        data[uid]["tuvi"] = 0
        save_data(data)
        await interaction.response.send_message(f"♻️ **Thiên Đạo** đã tẩy tủy cho **{user.display_name}**. Tu vi đã về 0, nhưng trang bị và vật phẩm vẫn giữ nguyên.")
    else:
        await interaction.response.send_message("❌ Tu sĩ này chưa nhập đạo.")

@bot.tree.command(name="reset_player", description="[Thiên Đạo] Xóa bỏ căn cơ, ép tu sĩ nhập đạo lại (Xóa sạch hết)")
async def reset_player(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id not in ADMIN_IDS:
        return await interaction.response.send_message("❌ Chỉ có Thiên Đạo mới có quyền xóa sổ đạo hạnh của người khác!", ephemeral=True)
    
    uid = str(user.id)
    data = load_data()
    
    if uid in data:
        del data[uid]
        save_data(data)
        await interaction.response.send_message(f"🧹 **Thiên Đạo** đã xóa sạch căn cơ của **{user.display_name}**. Người này giờ đã trở lại làm phàm nhân.")
    else:
        await interaction.response.send_message("❌ Người này vốn đã là phàm nhân.")

@bot.tree.command(name="add_linhthach", description="[Thiên Đạo] Ban phát hoặc thu hồi linh thạch")
async def add_linhthach(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not is_thien_dao(interaction.user.id):
        return await interaction.response.send_message("❌ Chỉ Thiên Đạo mới có quyền ban phát cơ duyên này!", ephemeral=True)
    
    uid = str(user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Tu sĩ này chưa nhập đạo.", ephemeral=True)
    
    data[uid]["linhthach"] += amount
    save_data(data)
    
    action = "ban tặng" if amount >= 0 else "thu hồi"
    await interaction.response.send_message(f"💎 **Thiên Đạo** đã {action} `{abs(amount)}` Linh Thạch cho **{user.display_name}**. Hiện có: `{data[uid]['linhthach']}`")

@bot.tree.command(name="add_vang", description="[Thiên Đạo] Ban tặng Vàng cho tu sĩ")
@app_commands.describe(user="Người được ban tặng", amount="Số lượng vàng")
async def add_vang(interaction: discord.Interaction, user: discord.Member, amount: int):
    # 1. Kiểm tra quyền Admin (Chỉ những ID trong ADMIN_IDS mới được dùng)
    if not is_thien_dao(interaction.user.id):
        return await interaction.response.send_message("❌ Chỉ Thiên Đạo mới có quyền ban phát cơ duyên này!", ephemeral=True)
    
    if amount <= 0:
        return await interaction.response.send_message("❌ Số lượng vàng phải lớn hơn 0!", ephemeral=True)

    uid = str(user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Tu sĩ này chưa nhập đạo.", ephemeral=True)

    # 2. Thực hiện cộng vàng
    old_gold = data[uid].get("gold", 0)
    data[uid]["gold"] = old_gold + amount
    
    save_data(data)
    
    # 3. Phản hồi bằng Embed cho trang trọng
    embed = discord.Embed(
        title="✨ ĐẠI NĂNG BAN LỘC",
        description=f"**Thiên Đạo** đã ban tặng 🪙 `{amount:,}` Vàng cho **{user.display_name}**!",
        color=0xffd700 # Màu vàng kim
    )
    embed.add_field(name="💰 Túi đồ hiện tại", value=f"🪙 `{data[uid]['gold']:,}` Vàng", inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="Đa tạ Thiên Đạo đã chiếu cố!")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="add_pet", description="[Thiên Đạo] Ban phát linh thú từ linh giới")
@app_commands.autocomplete(pet_name=pet_autocomplete) # Kết nối gợi ý vào tham số pet_name
async def add_pet(interaction: discord.Interaction, user: discord.Member, pet_name: str):
    if not is_thien_dao(interaction.user.id):
        return await interaction.response.send_message("❌ Chỉ Thiên Đạo mới có quyền ban phát cơ duyên này!", ephemeral=True)
    
    uid = str(user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Tu sĩ này chưa nhập đạo.", ephemeral=True)

    # Xử lý thu hồi linh thú
    if pet_name.lower() == "none":
        data[uid]["pet"] = "None"
        save_data(data)
        return await interaction.response.send_message(f"🌬️ **Thiên Đạo** đã thu hồi linh thú của **{user.display_name}**.")

    # Kiểm tra và ban tặng
    if pet_name in PET_DATA:
        pet_info = PET_DATA[pet_name]
        display_name = f"{pet_info['icon']} {pet_name} ({pet_info['rarity']})"
        data[uid]["pet"] = display_name
        msg = f"🐾 **Thiên Đạo** đã triệu hồi **{display_name}** ban cho **{user.display_name}**!"
    else:
        # Trường hợp đạo hữu tự nhập tên pet lạ không có trong danh sách
        data[uid]["pet"] = pet_name 
        msg = f"🐾 **Thiên Đạo** đã ban tặng Linh thú tự chế **[{pet_name}]** cho **{user.display_name}**!"

    save_data(data)
    await interaction.response.send_message(msg)

@bot.tree.command(name="add_trangbi", description="[Thiên Đạo] Ban phát pháp bảo từ thượng giới")
@app_commands.describe(loai="Chọn loại trang bị", item_name="Chọn tên vật phẩm")
@app_commands.choices(loai=[
    app_commands.Choice(name="Mũ (Nón)", value="mu"),
    app_commands.Choice(name="Giáp (Áo)", value="giap"),
    app_commands.Choice(name="Găng Tay", value="gang"),
    app_commands.Choice(name="Giày", value="giay"),
    app_commands.Choice(name="Vũ Khí", value="vukhi"),
])
@app_commands.autocomplete(item_name=equipment_autocomplete)
async def add_trangbi(interaction: discord.Interaction, user: discord.Member, loai: str, item_name: str):
    if not is_thien_dao(interaction.user.id):
        return await interaction.response.send_message("❌ Chỉ Thiên Đạo mới có quyền mở Thiên Khố!", ephemeral=True)
    
    uid = str(user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Tu sĩ này chưa nhập đạo.", ephemeral=True)

    # 1. Tìm "Cấp độ" (Key) của món đồ dựa trên tên Admin chọn
    found_level = None
    if loai in EQUIPMENT_DATA:
        for level_key, info in EQUIPMENT_DATA[loai].items():
            if info["name"] == item_name:
                found_level = level_key # Sẽ lấy được "Cấp 1", "Cấp 10", v.v...
                break

    if found_level:
        # 2. Cập nhật vào đúng cấu trúc mà lệnh /tuido yêu cầu
        # Lệnh tuido của bạn đọc: user["trangbi"][slot]
        if "trangbi" not in data[uid]:
            data[uid]["trangbi"] = {}
            
        data[uid]["trangbi"][loai] = found_level
        
        # 3. Reset độ bền về 100% cho món đồ mới (tùy chọn)
        if "durability" not in data[uid]:
            data[uid]["durability"] = {}
        data[uid]["durability"][loai] = 100

        save_data(data)
        
        msg = f"✨ **Thiên Đạo** đã ban tặng **{item_name}** ({found_level}) cho **{user.display_name}**!"
        await interaction.response.send_message(msg)
    else:
        await interaction.response.send_message(f"❌ Vật phẩm `{item_name}` không tồn tại trong loại `{loai}`!", ephemeral=True)

# --- 1.7 Hàm kiểm tra Cooldown chung ---

def check_cooldown(user, cooldown_seconds):
    now = int(time.time())
    last_action = user.get("last_action", 0)
    rem = last_action - now
    if rem > 0:
        return rem
    return 0

#2: Xây dựng, Hàm tiện ích

# --- 2.1 Quản lý File ---

def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_vn_now():
    return datetime.now(VN_TZ)

def get_today_str():
    return get_vn_now().strftime("%Y-%m-%d")

def get_seconds_until_midnight():
    now = get_vn_now()
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((next_midnight - now).total_seconds())

def format_seconds(seconds: int) -> str:
    seconds = max(0, int(seconds))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}ph")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)

def is_thien_dao(user_id: int) -> bool:
    return user_id == THIEN_DAO_ID

def ensure_user_defaults(user):
    user.setdefault("name", "Vô Danh")
    user.setdefault("tuvi", 0)
    user.setdefault("gold", 0)
    user.setdefault("linhthach", 0)
    user.setdefault("pet", "None")
    user.setdefault("tui_do", {})
    user.setdefault("last_action", 0)
    user.setdefault("last_tuluyen", 0)
    user.setdefault("last_haiduoc", 0)
    user.setdefault("last_diemdanh", "")
    user.setdefault("injury_until", 0)
    user.setdefault("exp_ngay", 0)
    user.setdefault("last_reset_day", get_today_str())
    user.setdefault("trangbi", {
        "mu": "Cấp 1",
        "giap": "Cấp 1",
        "gang": "Cấp 1",
        "giay": "Cấp 1",
        "vukhi": "Cấp 1"
    })
    user.setdefault("durability", {
        "mu": 100,
        "giap": 100,
        "gang": 100,
        "giay": 100,
        "vukhi": 100
    })
    for slot in ["mu", "giap", "gang", "giay", "vukhi"]:
        user["trangbi"].setdefault(slot, "Cấp 1")
        user["durability"].setdefault(slot, 100)

def check_daily_reset(user):
    """Reset Linh khí ngày đúng 00:00 theo giờ Việt Nam."""
    today = get_today_str()
    last_reset = user.get("last_reset_day", "")

    if last_reset != today:
        user["exp_ngay"] = 0
        user["last_reset_day"] = today
        return True
    return False


def get_player_stats(user):
    """Tính tổng chỉ số từ cảnh giới + trang bị chưa hỏng."""
    ensure_user_defaults(user)

    idx = get_rank_index(user.get("tuvi", 0))
    total_atk = 30 + idx * 40
    total_def = 20 + idx * 30
    total_hp = 200 + idx * 250

    for slot, cap_do in user.get("trangbi", {}).items():
        if slot not in EQUIPMENT_DATA or cap_do not in EQUIPMENT_DATA[slot]:
            continue
        if user.get("durability", {}).get(slot, 100) <= 0:
            continue
        item = EQUIPMENT_DATA[slot][cap_do]
        total_atk += item.get("atk", 0)
        total_def += item.get("def", 0)
        total_hp += item.get("hp", 0)

    return {"atk": total_atk, "def": total_def, "hp": total_hp}

# --- 2.2 Hàm xác định Cảnh giới hiện tại ---
def get_rank_index(tuvi):
    """Trả về vị trí (index) của cảnh giới dựa trên tu vi hiện tại"""
    for i, rank in enumerate(RANKS):
        if tuvi < rank["max"]:
            return i
    return len(RANKS) - 1

#3: Hệ thống Tu luyện & Đột phá

# --- 3.1 Hàm tìm Cảnh giới dựa trên Tu vi ---
def get_rank_index(tuvi):
    for i, rank in enumerate(RANKS):
        if tuvi < rank["max"]:
            return i
    return len(RANKS) - 1

# --- 3.2 Lệnh Tu luyện (Tích lũy đến giới hạn) ---
@bot.tree.command(name="tutien", description="Tọa thiền tại nhà (Delay 3 phút - Chung với Tuluyen)")
async def tutien(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    data = load_data()

    if uid not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)

    user = data[uid]
    ensure_user_defaults(user)
    check_daily_reset(user)
    now = int(time.time())

    injury_until = user.get("injury_until", 0)
    if now < injury_until:
        rem_injury = int((injury_until - now) / 60)
        save_data(data)
        return await interaction.response.send_message(
            f"❌ Đạo hữu đang bị **trọng thương** sau trận chiến Boss, không thể **Tu Tiên**! Cần nghỉ ngơi thêm **{rem_injury} phút**.",
            ephemeral=True
        )

    exp_ngay = user.get("exp_ngay", 0)
    if exp_ngay >= MAX_LINH_KHI_NGAY:
        save_data(data)
        return await interaction.response.send_message(
            f"❌ Linh khí ngày đã đầy **{exp_ngay}/{MAX_LINH_KHI_NGAY}**. Hãy chờ **00:00 giờ Việt Nam** để hệ thống reset.\n🕛 Còn lại: **{format_seconds(get_seconds_until_midnight())}**.",
            ephemeral=True
        )

    last_action = user.get("last_action", 0)
    if now < last_action and interaction.user.id not in ADMIN_IDS:
        rem = int(last_action - now)
        save_data(data)
        return await interaction.response.send_message(
            f"⏳ Đạo hữu đang tịnh tâm, hãy quay lại sau **{format_seconds(rem)}**.",
            ephemeral=True
        )

    idx = get_rank_index(user["tuvi"])
    current_rank = RANKS[idx]
    if user["tuvi"] >= current_rank["max"] - 1:
        save_data(data)
        return await interaction.response.send_message(f"⚡ Đỉnh phong rồi. Hãy `/dotpha`!", ephemeral=True)

    base_exp = random.randint(10, 35)
    gold_receive = random.randint(50, 150)
    final_exp = base_exp
    bonus_msg = ""
    raw_pet = user.get("pet")
    pet_display = str(raw_pet) if raw_pet is not None else "None"

    for pet_name, pet_info in PET_DATA.items():
        if pet_name in pet_display:
            multiplier = pet_info.get("bonus_exp", 1.0)
            if multiplier > 1.0:
                final_exp = int(base_exp * multiplier)
                bonus_msg = f"\n*(Nhờ {pet_info['icon']} {pet_name} trợ tu: **x{multiplier}** EXP)*"
            break

    actual_exp = min(final_exp, MAX_LINH_KHI_NGAY - exp_ngay)
    if actual_exp <= 0:
        save_data(data)
        return await interaction.response.send_message(
            f"❌ Linh khí ngày đã đầy **{exp_ngay}/{MAX_LINH_KHI_NGAY}**. Hãy chờ sang ngày mới.",
            ephemeral=True
        )

    user["tuvi"] = min(user["tuvi"] + actual_exp, current_rank["max"] - 1)
    user["exp_ngay"] = min(exp_ngay + actual_exp, MAX_LINH_KHI_NGAY)
    user["gold"] = user.get("gold", 0) + gold_receive
    user["last_action"] = now + 180

    save_data(data)

    embed = discord.Embed(
        title="🧘 TỌA THIỀN TU LUYỆN",
        description=f"**{interaction.user.display_name}** vừa kết thúc một chu kỳ tịnh tâm.",
        color=0x3498db
    )

    val_exp = f"`{actual_exp}` Tu vi"
    if bonus_msg:
        val_exp += f" {bonus_msg}"
    if actual_exp < final_exp:
        val_exp += f"\n*(Chạm trần linh khí ngày, chỉ hấp thu thêm **{actual_exp}**)*"

    embed.add_field(name="✨ Kết quả", value=val_exp, inline=True)
    embed.add_field(name="🪙 Vàng", value=f"`+{gold_receive}`", inline=True)
    embed.add_field(name="📊 Linh khí ngày", value=f"`{user['exp_ngay']}/{MAX_LINH_KHI_NGAY}`", inline=False)
    embed.set_footer(text="⏳ Cần nghỉ ngơi 3 phút để hồi phục linh lực")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="tuluyen", description="Ra ngoài diệt quái (Delay 5 phút - Chung với Tutien)")
async def tuluyen(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    data = load_data()

    if uid not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)

    user = data[uid]
    ensure_user_defaults(user)
    check_daily_reset(user)
    now = int(time.time())

    injury_until = user.get("injury_until", 0)
    if now < injury_until:
        rem_injury = int((injury_until - now) / 60)
        save_data(data)
        return await interaction.response.send_message(
            f"❌ Kinh mạch đang rối loạn do **trọng thương**, không thể **Tu Luyện**! Hãy đợi **{rem_injury} phút** nữa.",
            ephemeral=True
        )

    exp_ngay = user.get("exp_ngay", 0)
    if exp_ngay >= MAX_LINH_KHI_NGAY:
        save_data(data)
        return await interaction.response.send_message(
            f"❌ Linh khí ngày đã đầy **{exp_ngay}/{MAX_LINH_KHI_NGAY}**. Hãy chờ **00:00 giờ Việt Nam** để hệ thống reset.\n🕛 Còn lại: **{format_seconds(get_seconds_until_midnight())}**.",
            ephemeral=True
        )

    last_action = user.get("last_action", 0)
    if now < last_action and interaction.user.id not in ADMIN_IDS:
        rem = int(last_action - now)
        save_data(data)
        return await interaction.response.send_message(
            f"⚔️ Đạo hữu vừa đại chiến xong, thể lực chưa hồi phục! Hãy nghỉ ngơi thêm **{format_seconds(rem)}**.",
            ephemeral=True
        )

    dur_vukhi = user["durability"].get("vukhi", 100)
    if dur_vukhi <= 0:
        save_data(data)
        return await interaction.response.send_message("❌ Vũ khí nát vụn rồi, hãy `/suado` ngay!", ephemeral=True)

    slot_icons = {"mu": "👑", "giap": "🛡️", "gang": "🥊", "giay": "👞", "vukhi": "⚔️"}
    base_win_rate = 0.70
    penalty = (100 - dur_vukhi) / 200 if dur_vukhi < 100 else 0
    current_win_rate = base_win_rate - penalty
    win = random.random() < current_win_rate

    bai_quai = random.choice(BAI_QUAI)
    slots = list(slot_icons.keys())
    num_damaged = random.randint(3, 4)
    damaged_slots = random.sample(slots, num_damaged)
    embed = discord.Embed(color=0x00ff00 if win else 0xff0000)

    if win:
        base_exp = random.randint(55, 100)
        gold_gain = random.randint(200, 400)
        final_exp = base_exp
        raw_pet = user.get("pet")
        pet_display = str(raw_pet) if raw_pet is not None else "None"
        bonus_text = ""

        for pet_name, pet_info in PET_DATA.items():
            if pet_name in pet_display:
                multiplier = pet_info.get("bonus_exp", 1.0)
                final_exp = int(base_exp * multiplier)
                if multiplier > 1.0:
                    bonus_text = f" (Nhờ {pet_info['icon']} {pet_name} trợ giúp: x{multiplier} EXP)"
                break

        actual_exp = min(final_exp, MAX_LINH_KHI_NGAY - exp_ngay)
        user["tuvi"] = min(user["tuvi"] + actual_exp, RANKS[get_rank_index(user["tuvi"])] ["max"] - 1)
        user["exp_ngay"] = min(exp_ngay + actual_exp, MAX_LINH_KHI_NGAY)
        user["gold"] = user.get("gold", 0) + gold_gain

        embed.title = f"⚔️ {interaction.user.display_name} đại thắng tại {bai_quai}!"
        embed.description = (
            f"✨ Nhận: `{actual_exp}` Tu vi{bonus_text}\n"
            f"🪙 Nhận: `{gold_gain}` Vàng.\n"
            f"📉 **Hao tổn ({num_damaged} trang bị):**"
        )
        if actual_exp < final_exp:
            embed.description += f"\n🕯️ Chạm trần linh khí ngày, chỉ hấp thu thêm `{actual_exp}` tu vi."

        for slot in damaged_slots:
            loss = random.randint(15, 35)
            user["durability"][slot] = max(0, user["durability"][slot] - loss)
            embed.description += f"\n• {slot_icons[slot]} {slot.upper()}: `-{loss}%` (Còn {user['durability'][slot]}%)"
    else:
        exp_loss = random.randint(20, 50)
        user["tuvi"] = max(0, user["tuvi"] - exp_loss)

        embed.title = f"💀 Bại trận tại {bai_quai}..."
        embed.description = (
            f"❌ Tổn thất: `{exp_loss}` Tu vi.\n"
            f"❗ **Hư hỏng nặng ({num_damaged} trang bị):**"
        )

        for slot in damaged_slots:
            loss = random.randint(40, 60)
            user["durability"][slot] = max(0, user["durability"][slot] - loss)
            embed.description += f"\n• {slot_icons[slot]} {slot.upper()}: `-{loss}%` (Còn {user['durability'][slot]}%)"

    user["last_action"] = now + 300
    save_data(data)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="haiduoc", description="Cùng Linh thú vào rừng hái dược (1 tiếng/lần - Nhận 5-20 Linh Thạch)")
async def haiduoc(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)
    
    user = data[uid]
    ensure_user_defaults(user)
    check_daily_reset(user)
    now = int(time.time())

    # --- 1. KIỂM TRA COOLDOWN (1 TIẾNG) ---
    last_haiduoc = user.get("last_haiduoc", 0) 
    if now < last_haiduoc and interaction.user.id not in ADMIN_IDS:
        rem = last_haiduoc - now
        phut = rem // 60
        giay = rem % 60
        return await interaction.response.send_message(f"⏳ Thể lực cạn kiệt, hãy quay lại sau **{phut}ph {giay}s**.", ephemeral=True)

    # --- 2. LOGIC HÁI DƯỢC (5-20 LINH THẠCH) ---
    base_lt = random.randint(5, 20) # Giới hạn 5-20 theo lệnh của Tông chủ
    final_lt = base_lt
    bonus_msg = ""
    
    raw_pet = user.get("pet")
    pet_display = str(raw_pet) if raw_pet is not None else "None"
    
    for pet_name, pet_info in PET_DATA.items():
        if pet_name in pet_display:
            multiplier = pet_info.get("bonus_exp", 1.0)
            if multiplier > 1.0:
                # Nhân hệ số linh thú và ép kiểu số nguyên
                final_lt = int(base_lt * multiplier)
                bonus_msg = f"\n*(Nhờ {pet_info['icon']} {pet_name}: **x{multiplier}** linh thạch)*"
            break

    # --- 3. CẬP NHẬT DỮ LIỆU ---
    if "linhthach" not in user:
        user["linhthach"] = 0
        
    user["linhthach"] += final_lt
    user["last_haiduoc"] = now + 3600 
    save_data(data)

    # --- 4. PHẢN HỒI ---
    embed = discord.Embed(
        title="🌿 HÁI DƯỢC TẦM BẢO",
        description=f"**{interaction.user.display_name}** vừa tìm thấy dược liệu quý giá!",
        color=0x1abc9c
    )
    embed.add_field(name="💎 Linh Thạch nhận được", value=f"`+{final_lt}` viên {bonus_msg}", inline=False)
    embed.add_field(name="🎒 Tổng kho", value=f"`{user['linhthach']}` Linh Thạch", inline=True)
    
    embed.set_footer(text="⏳ Cần nghỉ ngơi 1 tiếng để hồi phục thể lực")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)
    
# --- 3.3 Lệnh Đột phá (Chính thức thăng cấp - Bản nâng cấp độ khó) ---
@bot.tree.command(name="dotpha", description="Vượt qua bình cảnh để thăng cấp cảnh giới")
async def dotpha(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    data = load_data()
    
    if uid not in data: return
    
    user = data[uid]
    ensure_user_defaults(user)
    check_daily_reset(user)
    save_data(data)
    idx = get_rank_index(user["tuvi"])
    current_rank = RANKS[idx]

    # 1. Kiểm tra điều kiện Tu vi (Phải đạt sát nút Max)
    if user["tuvi"] < current_rank["max"] - 1:
        con_thieu = (current_rank["max"] - 1) - user["tuvi"]
        return await interaction.response.send_message(
            f"⚠️ Căn cơ chưa vững! Cần thêm `{con_thieu}` Tu vi để đạt tới bình cảnh **{current_rank['name']}**.", 
            ephemeral=True
        )

    # 2. Thiết lập Tỷ lệ thành công & Hình phạt đặc biệt
    # Mặc định: Giảm dần theo cấp độ
    success_rate = max(5, 90 - (idx * 10))
    penalty_rate = 0.1 # Mặc định phạt 10% tu vi
    fail_msg = "Ngươi bị tẩu hỏa nhập ma!"

    # --- ĐỘ KHÓ RIÊNG CHO KIM ĐAN -> NGUYÊN ANH ---
    if current_rank["name"] == "Kim Đan":
        success_rate = 30  # Chỉ 30% thành công (Cực khó)
        penalty_rate = 0.2 # Thất bại phạt nặng hơn (20%)
        fail_msg = "⚡ THIÊN KIẾP GIÁNG XUỐNG! Sấm sét phá tan Kim Đan, tu vi tổn thất nặng nề!"
    
    # --- ĐỘ KHÓ CHO CÁC CẤP CAO (Độ Kiếp, Tiên Nhân) ---
    elif idx >= 8: 
        success_rate = 15  # Cảnh giới đỉnh cao chỉ có 15%
        penalty_rate = 0.25
        fail_msg = "💀 Đạo quả vỡ tan! Suýt nữa thì hồn phi phách tán!"

    # 3. Tiến hành quay số đột phá
    if random.randint(1, 100) <= success_rate:
        # THÀNH CÔNG
        user["tuvi"] = current_rank["max"] 
        next_rank_name = RANKS[min(idx + 1, len(RANKS)-1)]["name"]
        
        embed = discord.Embed(
            title="✨ ĐỘT PHÁ THÀNH CÔNG",
            description=f"Chúc mừng đạo hữu đã phá vỡ xiềng xích, bước vào cảnh giới **{next_rank_name}**!",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Tỷ lệ thành công vừa rồi: {success_rate}%")
    else:
        # THẤT BẠI
        loss = int(user["tuvi"] * penalty_rate)
        user["tuvi"] -= loss
        embed = discord.Embed(
            title="⚡ ĐỘT PHÁ THẤT BẠI",
            description=f"{fail_msg}\n📉 Tổn hao: `{loss}` Tu vi.",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Tỷ lệ thành công: {success_rate}% - Hãy kiên trì tu luyện lại!")
    
    save_data(data)
    await interaction.response.send_message(embed=embed)

#4: Hệ thống Nhập Đạo & Thông Tin Nhân Vật

# --- 4.1 Lệnh Nhập Đạo (Khởi tạo tài khoản) ---
@bot.tree.command(name="nhapdao", description="Bắt đầu con đường tu tiên")
async def nhapdao(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    data = load_data()
    
    # Lấy Biệt danh tại máy chủ (Nickname), nếu không có sẽ lấy Username
    ten_tu_si = interaction.user.display_name
    
    if uid in data:
        return await interaction.response.send_message(f"🙏 Đạo hữu **{ten_tu_si}** đã nhập đạo rồi, không nên tham lam bái sư nhiều lần!", ephemeral=True)
    
    # Khởi tạo dữ liệu mặc định: tặng 1000 Vàng và 20 Linh Thạch
    data[uid] = {
        "name": ten_tu_si,
        "tuvi": 0,
        "gold": 1000,
        "linhthach": 20,
        "trangbi": {
            "mu": "Cấp 1",
            "giap": "Cấp 1",
            "gang": "Cấp 1",
            "giay": "Cấp 1",
            "vukhi": "Cấp 1"
        },
        "durability": {
            "mu": 100,
            "giap": 100,
            "gang": 100,
            "giay": 100,
            "vukhi": 100
        },
        "tui_do": {},
        "pet": "None",
        "last_tuluyen": 0,
        "last_action": 0,
        "last_haiduoc": 0,
        "last_diemdanh": "",
        "injury_until": 0,
        "exp_ngay": 0,
        "last_reset_day": get_today_str()
    }
    
    save_data(data)
    
    embed = discord.Embed(
        title="✨ CHÚC MỪNG NHẬP ĐẠO ✨",
        description=(
            f"Chào mừng **{ten_tu_si}** đã bước chân vào con đường nghịch thiên cải mệnh!\n\n"
            f"🎁 Tông môn tặng ngươi:\n"
            f"🪙 **1,000 Vàng**\n"
            f"💎 **20 Linh Thạch**\n"
            f"⚔️ **Bộ trang bị tân thủ**"
        ),
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)

# --- 4.2 Lệnh Túi Đồ / Thông Tin (Xem trạng thái) ---

@bot.tree.command(name="tuido", description="Xem thông tin nhân vật và trang bị")
async def tuido(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)
    
    user = data[uid]
    ensure_user_defaults(user)
    check_daily_reset(user)
    save_data(data)

    idx = get_rank_index(user["tuvi"])
    rank = RANKS[idx]
    stats = get_player_stats(user)

    embed = discord.Embed(
        title=f"📜 BẢNG TRẠNG THÁI: {interaction.user.display_name}",
        color=0xffd700
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    embed.add_field(name="📖 Cảnh Giới", value=f"✨ **{rank['name']}**", inline=True)
    embed.add_field(name="📈 Tu Vi", value=f"**{user['tuvi']}/{rank['max']}**", inline=True)
    embed.add_field(name="🐾 Linh thú", value=f"**{user.get('pet', 'None')}**", inline=True)
    embed.add_field(
        name="📊 Chỉ Số Chiến Đấu",
        value=(
            f"⚔️ ATK: **{stats['atk']:,}**\n"
            f"🛡️ DEF: **{stats['def']:,}**\n"
            f"❤️ HP: **{stats['hp']:,}**"
        ),
        inline=False
    )

    exp_ngay = user.get("exp_ngay", 0)
    max_exp_ngay = MAX_LINH_KHI_NGAY
    bar_length = 10
    filled_length = int(round(bar_length * exp_ngay / max_exp_ngay)) if max_exp_ngay else 0
    filled_length = min(bar_length, max(0, filled_length))
    bar = "▰" * filled_length + "▱" * (bar_length - filled_length)
    embed.add_field(
        name="📊 Linh Khí Ngày",
        value=f"`{bar}` **{exp_ngay}/{max_exp_ngay}**\n🕛 Reset sau: **{format_seconds(get_seconds_until_midnight())}**",
        inline=False
    )

    vang = user.get("gold", 0)
    tai_san_content = f"🪙 Vàng: **{vang:,}** | 💎 Linh Thạch: **{user.get('linhthach', 0):,}**\n"
    slot_icons = {"mu": "👑", "giap": "🛡️", "gang": "🥊", "giay": "👞", "vukhi": "⚔️"}
    durability_data = user.get("durability", {})
    equip_list = "\n🛡️ **Trang Bị Hiện Tại**\n"
    for slot, icon in slot_icons.items():
        level = user["trangbi"].get(slot, "Cấp 1")
        item_name = EQUIPMENT_DATA[slot].get(level, {}).get("name", "Không rõ")
        dur = durability_data.get(slot, 100)
        equip_list += f"{icon} 🟦 **[{level}]** {item_name} `(Độ Bền: {dur}%)` \n"

    embed.add_field(name="🎒 TÚI ĐỒ", value=tai_san_content + equip_list, inline=False)
    embed.set_footer(text="Khi linh khí đầy, hãy đột phá để thăng tiến!")
    await interaction.response.send_message(embed=embed)
# --- 4.3 Lệnh Điểm Danh (Nhận Quà Mỗi Ngày) ---

@bot.tree.command(name="diemdanh", description="Điểm danh nhận Linh Thạch và Vàng hàng ngày (Reset lúc 00:00)")
async def diemdanh(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo! Hãy dùng `/nhapdao` trước.", ephemeral=True)
    
    user = data[uid]
    
    # Lấy ngày hiện tại dưới dạng chuỗi (YYYY-MM-DD)
    ensure_user_defaults(user)
    check_daily_reset(user)
    today = get_today_str()
    
    # Kiểm tra xem hôm nay đã điểm danh chưa
    last_checkin = user.get("last_diemdanh", "")
    
    if last_checkin == today:
        # Tính toán thời gian còn lại đến 12h đêm nay để báo cho đệ tử
        msg = f"❌ Hôm nay đạo hữu đã điểm danh rồi! Hãy quay lại sau **{format_seconds(get_seconds_until_midnight())}** nữa."
        return await interaction.response.send_message(msg, ephemeral=True)

    # Thưởng: 50-100 Vàng và 5-10 Linh Thạch (Tông chủ có thể chỉnh lại số lượng)
    gold_reward = random.randint(500, 1000)
    stone_reward = random.randint(10, 20)
    
    # Cập nhật dữ liệu
    user["gold"] = user.get("gold", 0) + gold_reward
    user["linhthach"] = user.get("linhthach", 0) + stone_reward
    user["last_diemdanh"] = today  # Đánh dấu đã điểm danh ngày hôm nay
    
    # Reset linh khí/exp ngày khi điểm danh ngày mới
    #user["exp_ngay"] = 0 
    
    save_data(data)
    
    embed = discord.Embed(
        title="🧧 ĐIỂM DANH TÔNG MÔN",
        description=f"Chúc mừng **{interaction.user.display_name}** đã hoàn thành điểm danh ngày hôm nay!",
        color=0xffd700
    )
    embed.add_field(name="💰 Vàng nhận được", value=f"`+{gold_reward}`", inline=True)
    embed.add_field(name="💎 Linh Thạch nhận được", value=f"`+{stone_reward}`", inline=True)
    embed.set_footer(text=f"Tài sản hiện có: {user['gold']} Vàng | {user['linhthach']} Linh Thạch")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

#5: Hệ thống Trang Bị & GACHA
    
# --- 5.1 Sửa Trang Bị ---
@bot.tree.command(name="suado", description="Dùng Vàng để đại tu toàn bộ trang bị (1% độ bền = 10 Vàng)")
async def suado(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)
    
    user = data[uid]
    durability_data = user.get("durability", {"mu": 100, "giap": 100, "gang": 100, "giay": 100, "vukhi": 100})
    slot_icons = {"mu": "👑", "giap": "🛡️", "gang": "🥊", "giay": "👞", "vukhi": "⚔️"}
    
    total_repair_cost = 0
    repaired_items = []

    # Tính toán chi phí sửa chữa cho từng món đồ bị hỏng
    for slot, dur in durability_data.items():
        if dur < 100:
            # Công thức: Mỗi 1% độ bền thiếu hụt tốn 10 Vàng
            cost = (100 - dur) * 10 
            total_repair_cost += cost
            repaired_items.append(f"{slot_icons[slot]} {slot.upper()}")

    # 1. Kiểm tra nếu không có đồ hỏng
    if not repaired_items:
        return await interaction.response.send_message("✨ Trang bị của đạo hữu vẫn còn rất tốt, không cần sửa chữa!", ephemeral=True)

    # 2. Kiểm tra túi tiền
    current_gold = user.get("gold", 0)
    if current_gold < total_repair_cost:
        return await interaction.response.send_message(
            f"❌ Không đủ Vàng! Cần `{total_repair_cost:,}` Vàng để sửa toàn bộ, đạo hữu chỉ có `{current_gold:,}`.", 
            ephemeral=True
        )

    # 3. Thực hiện sửa đồ
    user["gold"] = current_gold - total_repair_cost
    for slot in durability_data:
        durability_data[slot] = 100 # Phục hồi về 100%
    
    user["durability"] = durability_data
    save_data(data)

    # 4. Phản hồi kết quả
    items_str = ", ".join(repaired_items)
    await interaction.response.send_message(
        f"🛠️ **Thợ rèn** đã nhận `{total_repair_cost:,}` Vàng và đại tu: {items_str} cho **{interaction.user.display_name}**!\n"
        f"✨ Tất cả trang bị đã hồi phục về **100%** độ bền. Sẵn sàng chinh chiến!"
    )

# --- 5.2 Gacha ---

@bot.tree.command(name="gacha_pet", description="Triệu hồi linh thú (10 Linh Thạch/lần - Tối đa x5)")
@app_commands.describe(solan="Số lần triệu hồi (từ 1 đến 5)")
async def gacha_pet(interaction: discord.Interaction, solan: int = 1):
    uid = str(interaction.user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)
    
    if not (1 <= solan <= 5):
        return await interaction.response.send_message("❌ Mỗi lần chỉ có thể triệu hồi từ 1 đến 5 linh thú!", ephemeral=True)
    
    user = data[uid]
    cost_per_roll = 10
    total_cost = cost_per_roll * solan
    
    if user.get("linhthach", 0) < total_cost:
        return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần `{total_cost}` viên.", ephemeral=True)

    # Lấy thông tin Pet hiện tại
    current_pet_name = ""
    current_tier = 0
    
    raw_pet = user.get("pet")
    pet_display = str(raw_pet) if raw_pet is not None else "None"
    
    for p_name, p_info in PET_DATA.items():
        if p_name in pet_display:
            current_pet_name = p_name
            current_tier = p_info.get("tier", 0)
            break

    # Logic Gacha
    pets_pool = list(PET_DATA.keys())
    weights = [PET_DATA[p]["rate"] for p in pets_pool]
    if sum(weights) < 100:
        pets_pool.append("Trượt")
        weights.append(100 - sum(weights))

    results = []
    user["linhthach"] -= total_cost
    refund_total = 0
    new_pet_assigned = None
    max_tier_in_roll = current_tier
    hit_legendary = False

    for i in range(solan):
        res = random.choices(pets_pool, weights=weights, k=1)[0]
        
        if res == "Trượt":
            results.append(f"Lần {i+1}: ☁️ Luồng linh khí tan biến...")
            continue

        pet_info = PET_DATA[res]
        res_display = f"{pet_info['icon']} {res} ({pet_info['rarity']})"

        # TRƯỜNG HỢP 1: Trùng con đang có (Cùng loại)
        if res == current_pet_name:
            refund = random.randint(2, 5)
            refund_total += refund
            results.append(f"Lần {i+1}: ✨ **{res_display}** (Trùng - Hoàn `{refund}` Linh Thạch)")
        
        # TRƯỜNG HỢP 2: Trúng con mới có Tier cao hơn
        elif pet_info["tier"] > max_tier_in_roll:
            new_pet_assigned = res_display
            max_tier_in_roll = pet_info["tier"]
            results.append(f"Lần {i+1}: 🌟 **{res_display}** (Bậc cao hơn - Đã nhận)")
            if res == "Cửu Vĩ Hồ": hit_legendary = True
            
        # TRƯỜNG HỢP 3: Tier thấp hơn con đang có
        else:
            results.append(f"Lần {i+1}: 🍃 **{res_display}** (Cấp thấp - Đã thả đi)")

    # Cập nhật dữ liệu
    if new_pet_assigned:
        user["pet"] = new_pet_assigned
    user["linhthach"] += refund_total
    save_data(data)

    # Phản hồi Embed
    embed = discord.Embed(
        title="🎊 [DỊ TƯỢNG] THẦN THÚ XUẤT THẾ! 🎊" if hit_legendary else f"🔮 ĐÀI TRIỆU HỒI LINH THÚ (x{solan})",
        color=0xff00ff if hit_legendary else (0xffd700 if new_pet_assigned else 0x808080)
    )
    
    desc = f"**{interaction.user.display_name}** tiêu hao `{total_cost}` Linh Thạch.\n\n" + "\n".join(results)
    if refund_total > 0:
        desc += f"\n\n💰 Tổng linh thạch hoàn lại: `{refund_total}` viên."
    
    embed.description = desc
    
    embed.set_footer(text=f"💎 Linh Thạch còn lại: {user['linhthach']} viên")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="gacha_trangbi", description="Triệu hồi trang bị (15 Linh Thạch/lần - Tối đa x5)")
@app_commands.describe(solan="Số lần triệu hồi (từ 1 đến 5)")
async def gacha_trangbi(interaction: discord.Interaction, solan: int = 1):
    uid = str(interaction.user.id)
    data = load_data()
    
    if uid not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)
    
    if not (1 <= solan <= 5):
        return await interaction.response.send_message("❌ Mỗi lần chỉ có thể triệu hồi từ 1 đến 5 trang bị!", ephemeral=True)
    
    user = data[uid]
    cost_per_roll = 15
    total_cost = cost_per_roll * solan
    
    if user.get("linhthach", 0) < total_cost:
        return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần `{total_cost}` viên.", ephemeral=True)

    # 1. Thiết lập tỉ lệ xuất hiện cấp độ (Cấp 7-10 cực khó)
    levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    weights = [25, 20, 18, 15, 10, 6, 3.5, 1.5, 0.7, 0.3] 
    
    slots = ["mu", "giap", "gang", "giay", "vukhi"]
    slot_icons = {"mu": "👑", "giap": "🛡️", "gang": "🥊", "giay": "👞", "vukhi": "⚔️"}
    
    results = []
    user["linhthach"] -= total_cost
    items_replaced = []

    for i in range(solan):
        selected_lv = random.choices(levels, weights=weights, k=1)[0]
        selected_slot = random.choice(slots)
        level_key = f"Cấp {selected_lv}"
        
        # Lấy tên trang bị từ EQUIPMENT_DATA
        item_name = EQUIPMENT_DATA[selected_slot][level_key]["name"]
        display_item = f"{slot_icons[selected_slot]} {item_name} ({level_key})"
        
        # Kiểm tra với đồ đang mặc
        current_item_str = user["trangbi"].get(selected_slot, "Cấp 1")
        current_lv = int(current_item_str.split(" ")[1])
        
        if selected_lv > current_lv:
            if "durability" not in user:
                user["durability"] = {"mu": 100, "giap": 100, "gang": 100, "giay": 100, "vukhi": 100}
            
            user["trangbi"][selected_slot] = level_key
            user["durability"][selected_slot] = 100 # Giờ đã an toàn để gán 100%
            items_replaced.append(display_item)
            status = "✨ **Đã mặc**"
        else:
            status = "🍃 *Phế liệu*"
            
        # Hiệu ứng màu sắc cho trang bị xịn
        if selected_lv >= 7:
            results.append(f"Lần {i+1}: 🌈 **{display_item}** - {status}")
        else:
            results.append(f"Lần {i+1}: {display_item} - {status}")

    save_data(data)

    # 2. Phản hồi Embed
    is_legendary = any("Cấp 10" in res for res in results)
    embed = discord.Embed(
        title=f"🎁 KHO BÁU TÔNG MÔN (x{solan})",
        color=0xff00ff if is_legendary else 0x00ff00
    )
    
    embed.description = f"**{interaction.user.display_name}** tiêu hao `{total_cost}` Linh Thạch:\n\n" + "\n".join(results)
    
    if items_replaced:
        embed.add_field(name="🆕 Trang bị mới", value="\n".join(items_replaced), inline=False)
    
    embed.set_footer(text=f"💎 Linh Thạch còn lại: {user['linhthach']} | Độ bền đồ mới: 100%")
    
    await interaction.response.send_message(embed=embed)


# --- 5.3 Giao Dịch ---

@bot.tree.command(name="chuyenvang", description="Chuyển Vàng cho đạo hữu khác")
@app_commands.describe(nguoi_nhan="Người nhận vàng", so_luong="Số lượng vàng muốn chuyển")
async def chuyenvang(interaction: discord.Interaction, nguoi_nhan: discord.Member, so_luong: int):
    uid_gui = str(interaction.user.id)
    uid_nhan = str(nguoi_nhan.id)
    data = load_data()

    # 1. Kiểm tra điều kiện cơ bản
    if uid_gui not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)
    if uid_nhan not in data:
        return await interaction.response.send_message("❌ Người nhận chưa gia nhập tông môn!", ephemeral=True)
    if uid_gui == uid_nhan:
        return await interaction.response.send_message("❌ Ngươi định tay trái chuyển sang tay phải sao? Không thể tự chuyển cho mình!", ephemeral=True)
    if so_luong <= 0:
        return await interaction.response.send_message("❌ Số lượng chuyển phải lớn hơn 0!", ephemeral=True)

    user_gui = data[uid_gui]
    user_nhan = data[uid_nhan]

    # 2. Kiểm tra số dư
    vang_hien_co = user_gui.get("gold", 0)
    if vang_hien_co < so_luong:
        return await interaction.response.send_message(f"❌ Ngươi không đủ Vàng! Hiện có: `{vang_hien_co}`", ephemeral=True)

    # 3. Thực hiện giao dịch
    user_gui["gold"] -= so_luong
    user_nhan["gold"] = user_nhan.get("gold", 0) + so_luong
    save_data(data)

    # 4. Phản hồi
    embed = discord.Embed(
        title="💸 GIAO DỊCH VÀNG",
        description=f"**{interaction.user.display_name}** đã chuyển vàng thành công!",
        color=0xf1c40f
    )
    embed.add_field(name="👤 Người nhận", value=nguoi_nhan.mention, inline=True)
    embed.add_field(name="💰 Số lượng", value=f"`{so_luong}` Vàng", inline=True)
    embed.set_footer(text=f"Số dư còn lại: {user_gui['gold']} Vàng")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="chuyenlinhthach", description="Chuyển Linh Thạch cho đạo hữu khác")
@app_commands.describe(nguoi_nhan="Người nhận linh thạch", so_luong="Số lượng linh thạch muốn chuyển")
async def chuyenlinhthach(interaction: discord.Interaction, nguoi_nhan: discord.Member, so_luong: int):
    uid_gui = str(interaction.user.id)
    uid_nhan = str(nguoi_nhan.id)
    data = load_data()

    # 1. Kiểm tra điều kiện cơ bản
    if uid_gui not in data:
        return await interaction.response.send_message("❌ Ngươi chưa nhập đạo!", ephemeral=True)
    if uid_nhan not in data:
        return await interaction.response.send_message("❌ Người nhận chưa gia nhập tông môn!", ephemeral=True)
    if uid_gui == uid_nhan:
        return await interaction.response.send_message("❌ Không thể tự chuyển cho chính mình!", ephemeral=True)
    if so_luong <= 0:
        return await interaction.response.send_message("❌ Số lượng chuyển phải lớn hơn 0!", ephemeral=True)

    user_gui = data[uid_gui]
    user_nhan = data[uid_nhan]

    # 2. Kiểm tra số dư linh thạch
    lt_hien_co = user_gui.get("linhthach", 0)
    if lt_hien_co < so_luong:
        return await interaction.response.send_message(f"❌ Ngươi không đủ Linh Thạch! Hiện có: `{lt_hien_co}`", ephemeral=True)

    # 3. Thực hiện giao dịch
    user_gui["linhthach"] -= so_luong
    user_nhan["linhthach"] = user_nhan.get("linhthach", 0) + so_luong
    save_data(data)

    # 4. Phản hồi
    embed = discord.Embed(
        title="💎 GIAO DỊCH LINH THẠCH",
        description=f"**{interaction.user.display_name}** đã truyền Linh Thạch cho đạo hữu khác!",
        color=0x1abc9c
    )
    embed.add_field(name="👤 Người nhận", value=nguoi_nhan.mention, inline=True)
    embed.add_field(name="✨ Số lượng", value=f"`{so_luong}` viên", inline=True)
    embed.set_footer(text=f"Số dư còn lại: {user_gui['linhthach']} Linh Thạch")

    await interaction.response.send_message(embed=embed)


#6: Boss & Bí Cảnh
# --- 6.1 Boss ---

@bot.tree.command(name="boss", description="Tổ đội diệt Boss (Cần đồng đội xác nhận)")
@app_commands.autocomplete(boss_name=boss_autocomplete)
async def boss(interaction: discord.Interaction, boss_name: str, 
               dong_doi_1: discord.Member, 
               dong_doi_2: discord.Member = None, dong_doi_3: discord.Member = None, 
               dong_doi_4: discord.Member = None, dong_doi_5: discord.Member = None):
    if boss_name not in BOSS_DATA:
        return await interaction.response.send_message(f"❌ Boss `{boss_name}` không tồn tại!", ephemeral=True)

    raw_members = [interaction.user, dong_doi_1, dong_doi_2, dong_doi_3, dong_doi_4, dong_doi_5]
    team = list(dict.fromkeys([m for m in raw_members if m is not None]))

    if len(team) < 2:
        return await interaction.response.send_message("❌ Cần ít nhất 2 người để lập tổ đội đánh Boss!", ephemeral=True)

    data = load_data()
    now = time.time()

    for m in team:
        uid = str(m.id)
        if uid not in data:
            return await interaction.response.send_message(f"❌ {m.mention} chưa nhập đạo, không thể tham chiến!", ephemeral=True)

        u_data = data[uid]
        ensure_user_defaults(u_data)
        check_daily_reset(u_data)

        if now < u_data.get("injury_until", 0):
            return await interaction.response.send_message(f"❌ {m.mention} đang bị trọng thương, không thể tham chiến!", ephemeral=True)
        if u_data.get("last_boss_day") == get_today_str() and u_data.get("last_boss", 0) > 0:
            return await interaction.response.send_message(f"❌ {m.mention} đã hết lượt đánh Boss hôm nay!", ephemeral=True)

    save_data(data)

    view = BossConfirmView(interaction.user, team, boss_name)
    mentions = ", ".join([m.mention for m in team if m.id != interaction.user.id])
    await interaction.response.send_message(
        content=f"📜 **CHIẾN THƯ**\n{interaction.user.mention} triệu tập {mentions} đi tiêu diệt **{boss_name}**!",
        view=view
    )

    await view.wait()
    if not view.is_started:
        return

    try:
        data = load_data()
        now = time.time()
        boss_info = BOSS_DATA[boss_name]
        num_mem = len(team)
        mult = math.pow(boss_info.get("scale", 1.2), num_mem - 1)
        b_hp = int(boss_info["hp"] * mult)
        b_atk = int(boss_info["atk"] * mult)
        b_def = int(boss_info["def"] * mult)

        team_stats = []
        total_damage = 0
        total_hp = 0
        total_boss_counter = 0

        for m in team:
            uid = str(m.id)
            user = data[uid]
            ensure_user_defaults(user)
            check_daily_reset(user)
            pstats = get_player_stats(user)
            damage = max(1, pstats["atk"] - b_def // 4)
            taken = max(1, b_atk - pstats["def"] // 3)
            team_stats.append({
                "member": m,
                "uid": uid,
                "atk": pstats["atk"],
                "def": pstats["def"],
                "hp": pstats["hp"],
                "damage": damage,
                "taken": taken
            })
            total_damage += damage
            total_hp += pstats["hp"]
            total_boss_counter += taken

        is_win = total_damage >= b_hp and total_hp > total_boss_counter
        embed = discord.Embed(
            title=f"⚔️ KẾT QUẢ: {boss_name}",
            description="🎉 **ĐẠI THẮNG!** Tổ đội đã tru sát ma đầu." if is_win else "💀 **THẤT BẠI!** Tổ đội bị Boss đánh tan tác.",
            color=0x2ecc71 if is_win else 0xe74c3c
        )
        embed.add_field(name="👹 Boss", value=f"❤️ HP: **{b_hp:,}**\n⚔️ ATK: **{b_atk:,}**\n🛡️ DEF: **{b_def:,}**", inline=True)
        embed.add_field(name="👥 Tổ đội", value=f"Tổng damage: **{total_damage:,}**\nTổng HP: **{total_hp:,}**\nPhản đòn boss: **{total_boss_counter:,}**", inline=True)

        detail_lines = []
        for p in team_stats:
            detail_lines.append(
                f"{p['member'].mention}: ⚔️ `{p['atk']:,}` | 🛡️ `{p['def']:,}` | ❤️ `{p['hp']:,}` | 💥 `{p['damage']:,}` | 🩸 `{p['taken']:,}`"
            )
        embed.add_field(name="📜 Chiến Báo", value="\n".join(detail_lines), inline=False)

        if is_win:
            reward_lt = random.randint(*boss_info.get("reward_lt", (20, 50)))
            reward_gold = random.randint(3000, 7000)
            reward_tuvi = random.randint(500, 1000)
            reward_msg = []
            for m in team:
                uid = str(m.id)
                user = data[uid]
                ensure_user_defaults(user)
                current_rank = RANKS[get_rank_index(user.get("tuvi", 0))]
                user["tuvi"] = min(user.get("tuvi", 0) + reward_tuvi, current_rank["max"] - 1)
                user["linhthach"] = user.get("linhthach", 0) + reward_lt
                user["gold"] = user.get("gold", 0) + reward_gold
                user["last_boss"] = now
                user["last_boss_day"] = get_today_str()
                if random.random() < boss_info.get("drop_rate", 0.0):
                    loai = random.choice(["mu", "giap", "gang", "giay", "vukhi"])
                    cap_options = list(EQUIPMENT_DATA[loai].keys())
                    cap = random.choice(cap_options[max(0, len(cap_options)-3):])
                    user.setdefault("trangbi", {})[loai] = cap
                    user.setdefault("durability", {})[loai] = 100
                    reward_msg.append(f"⭐ {m.mention} nhận được **{EQUIPMENT_DATA[loai][cap]['name']}** ({cap})")
            embed.add_field(name="🎁 Phần thưởng mỗi người", value=f"✨ Tu Vi: **+{reward_tuvi:,}**\n💎 Linh Thạch: **+{reward_lt:,}**\n🪙 Vàng: **+{reward_gold:,}**", inline=False)
            if reward_msg:
                embed.add_field(name="🌟 Vật Phẩm Rơi Ra", value="\n".join(reward_msg), inline=False)
        else:
            fail_msg = []
            for m in team:
                uid = str(m.id)
                user = data[uid]
                ensure_user_defaults(user)
                lost_tuvi = random.randint(300, 700)
                user["tuvi"] = max(0, user.get("tuvi", 0) - lost_tuvi)
                for slot in user.get("durability", {}):
                    user["durability"][slot] = 0
                user["injury_until"] = now + 1800
                user["last_boss"] = now
                user["last_boss_day"] = get_today_str()
                fail_msg.append(f"• {m.mention}: -`{lost_tuvi}` Tu vi, toàn bộ trang bị về `0%`, trọng thương `30 phút`.")
            embed.add_field(name="📉 Tổn Thất", value="\n".join(fail_msg), inline=False)

        save_data(data)
        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"Lỗi tại lệnh Boss: {e}")
        try:
            await interaction.followup.send("❌ Pháp trận gặp trục trặc khi thảo phạt Boss!")
        except:
            pass
#7: Hệ thống HƯỚNG DẪN & BXH

# --- 7.1 Hướng Dẫn ---

@bot.tree.command(name="huongdan", description="Xem cẩm nang tu luyện dành cho tân thủ")
async def huongdan(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 CẨM NANG TU LUYỆN TÔNG MÔN",
        description="Chào mừng đạo hữu đã nhập đạo! Hãy đọc kỹ hướng dẫn dưới đây để sớm phi thăng.",
        color=0x3498db
    )

    # --- Mục 1: Khởi đầu ---
    embed.add_field(
        name="🛡️ 1. Khởi Đầu",
        value=(
            "• `/nhapdao`: Tạo hồ sơ tu tiên.\n"
            "• `/diemdanh`: Nhận Linh Thạch và Vàng mỗi ngày."
        ),
        inline=False
    )

    # --- Mục 2: Tu Luyện & Chiến Đấu ---
    embed.add_field(
        name="⚔️ 2. Tu Luyện & Thời Gian Nghỉ",
        value=(
            "• `/tutien`: Tọa thiền tích lũy (Nghỉ **3 phút**).\n"
            "• `/tuluyen`: Đánh quái luyện công (Nghỉ **5 phút**).\n"
            "• **Lưu ý:** Hai lệnh này dùng chung thời gian chờ (Cooldown)."
        ),
        inline=False
    )

    # --- Mục 3: Thảo Phạt Ma Đầu (MỚI) ---
    embed.add_field(
        name="👹 3. Thảo Phạt Ma Đầu",
        value=(
            "• `/bossinfo`: Xem chỉ số và phần thưởng của Boss.\n"
            "• `/boss`: Lập tổ đội (ít nhất 2 người) để diệt Boss.\n"
            "• **Hậu quả:** Thất bại sẽ bị **Trọng Thương 30 phút** (không thể tu luyện) và hư hỏng toàn bộ trang bị."
        ),
        inline=False
    )

    # --- Mục 4: Trang Bị & Linh Thú ---
    embed.add_field(
        name="🦊 4. Trang Bị & Linh Thú",
        value=(
            "• `/tuido`: Xem trang bị, linh thú và cảnh giới.\n"
            "• `/tbinfo`: Tra cứu toàn bộ chỉ số trang bị theo Cấp (1-9).\n"
            "• `/petinfo`: Xem chi tiết sức mạnh linh thú.\n"
            "• `/gacha_trangbi` & `/gacha_pet`: Tìm kiếm báu vật."
        ),
        inline=False
    )

    # --- Mục 5: Bảo Dưỡng ---
    embed.add_field(
        name="🔨 5. Bảo Dưỡng",
        value=(
            "• Trang bị hỏng (0%) sẽ không thể `/tuluyen`.\n"
            "• Dùng `/suado` (tốn Vàng) để phục hồi trang bị."
        ),
        inline=False
    )

    embed.set_footer(text="Chúc đạo hữu sớm đạt cảnh giới tối cao!")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)
    

# --- 7.2 BXH ---


# --- 7.3 Info Boss - Pet & Trang bị ---

@bot.tree.command(name="bossinfo", description="Xem thông tin chi tiết các Ma Đầu")
@app_commands.autocomplete(boss_name=boss_autocomplete)
async def bossinfo(interaction: discord.Interaction, boss_name: str):
    if boss_name not in BOSS_DATA:
        return await interaction.response.send_message(f"❌ Boss `{boss_name}` không tồn tại trong bí tịch!", ephemeral=True)

    boss = BOSS_DATA[boss_name]
    
    # Lấy thông tin phần thưởng từ BOSS_DATA
    # Giả sử cấu trúc BOSS_DATA của đạo hữu có các trường này
    hp = boss.get("hp", 0)
    atk = boss.get("atk", 0)
    defense = boss.get("def", 0)
    scale = boss.get("scale", 1.2)
    
    embed = discord.Embed(
        title=f"👹 THÔNG TIN MA ĐẦU: {boss_name}",
        description=f"*{boss.get('description', 'Một đại ma đầu đang ẩn mình trong bóng tối...') }*",
        color=0x9b59b6 # Màu tím huyền bí
    )
    
    # Hiển thị chỉ số cơ bản
    embed.add_field(name="❤️ Sinh Lực (HP)", value=f"`{hp:,}`", inline=True)
    embed.add_field(name="⚔️ Tấn Công (ATK)", value=f"`{atk:,}`", inline=True)
    embed.add_field(name="🛡️ Phòng Thủ (DEF)", value=f"`{defense:,}`", inline=True)
    
    # Hiển thị cơ chế tổ đội
    embed.add_field(
        name="📈 Độ Khó Tổ Đội", 
        value=f"Boss sẽ mạnh lên x{scale} theo mỗi thành viên tham gia.", 
        inline=False
    )
    
    # Hiển thị thông tin phần thưởng
    reward_text = (
        f"• **EXP**: 500 - 1000 (x2 khi có đồng đội)\n"
        f"• **Linh Thạch**: 20 - 50\n"
        f"• **Vàng**: 3000 - 7000\n"
        f"• **Tỉ lệ rơi Thần Khí (Cấp 8-9)**: 0.1%\n"
    )
    embed.add_field(name="🎁 Phần Thưởng Dự Kiến", value=reward_text, inline=False)
    
    # Hình phạt nếu thất bại
    penalty_text = (
        "• Khấu trừ 300 - 700 Tu vi\n"
        "• Hư hỏng toàn bộ trang bị (Độ bền về 0%)\n"
        "• Trạng thái **Trọng Thương** trong 30 phút\n"
    )
    embed.add_field(name="💀 Hình Phạt Khi Thất Bại", value=penalty_text, inline=False)

    embed.set_footer(text="Lời khuyên: Hãy lập tổ đội ít nhất 2 người để có cơ hội chiến thắng!")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="petinfo", description="Xem thông tin chi tiết về Linh Thú")
@app_commands.autocomplete(pet_name=pet_autocomplete) # Giả sử đạo hữu đã có autocomplete cho Pet
async def petinfo(interaction: discord.Interaction, pet_name: str):
    # Giả sử PET_DATA là nơi lưu thông tin các loại Pet
    if pet_name not in PET_DATA:
        return await interaction.response.send_message(f"❌ Linh thú `{pet_name}` không có trong danh lục!", ephemeral=True)

    pet = PET_DATA[pet_name]
    embed = discord.Embed(
        title=f"🐾 LINH THÚ: {pet_name}",
        description=f"*{pet.get('desc', 'Một sinh vật linh thiêng của trời đất.')}*",
        color=0x3498db
    )
    
    # Hiển thị các chỉ số cộng thêm cho chủ nhân
    embed.add_field(name="⚔️ Tăng Tấn Công", value=f"`+{pet.get('atk', 0)}`", inline=True)
    embed.add_field(name="🛡️ Tăng Phòng Thủ", value=f"`+{pet.get('def', 0)}`", inline=True)
    embed.add_field(name="❤️ Tăng Sinh Lực", value=f"`+{pet.get('hp', 0)}`", inline=True)
    
    # Nếu có kỹ năng đặc biệt
    if "skill" in pet:
        embed.add_field(name="✨ Tuyệt Kỹ", value=pet["skill"], inline=False)

    embed.set_footer(text="Linh thú càng mạnh, con đường tu tiên càng vững chãi!")
    await interaction.response.send_message(embed=embed)
    

@bot.tree.command(name="tbinfo", description="Xem toàn bộ bộ trang bị theo cấp bậc")
@app_commands.describe(cap="Chọn cấp bậc muốn xem (1-10)")
async def tbinfo(interaction: discord.Interaction, cap: int):
    # Chuẩn hóa định dạng cấp bậc
    cap_str = f"Cấp {cap}"
    
    embed = discord.Embed(
        title=f"📜 ĐẠI THƯ VIỆN TRANG BỊ: {cap_str}",
        description=f"Thông tin chi tiết bộ thần khí phẩm bậc **{cap_str}**",
        color=0xe67e22 # Màu cam đồng tông phẩm cấp
    )
    
    # Danh sách các loại trang bị và icon tương ứng
    slots = {
        "vukhi": ("⚔️", "Vũ Khí"),
        "giap": ("🛡️", "Giáp Trụ"),
        "mu": ("👑", "Mũ/Quán"),
        "gang": ("🥊", "Hộ Thủ"),
        "giay": ("👞", "Ngự Phong")
    }

    found_any = False
    for slot, (icon, label) in slots.items():
        if slot in EQUIPMENT_DATA and cap_str in EQUIPMENT_DATA[slot]:
            item = EQUIPMENT_DATA[slot][cap_str]
            
            # Gom chỉ số
            stats = []
            if "atk" in item: stats.append(f"ATK: `+{item['atk']:,}`")
            if "def" in item: stats.append(f"DEF: `+{item['def']:,}`")
            if "hp" in item: stats.append(f"HP: `+{item['hp']:,}`")
            
            stats_str = " | ".join(stats) if stats else "Không có chỉ số"
            
            embed.add_field(
                name=f"{icon} {label}: {item.get('name', 'Chưa đặt tên')}",
                value=stats_str,
                inline=False
            )
            found_any = True

    if not found_any:
        return await interaction.response.send_message(f"❌ Không tìm thấy dữ liệu cho **{cap_str}**!", ephemeral=True)

    embed.set_footer(text=f"Tông chủ Momo • Thư viện thần khí")
    await interaction.response.send_message(embed=embed)        

#8 Hệ thống BOT

# --- 8.1 ---
@bot.event
async def on_ready():
    print(f'He Thong Da Dang Nhap: {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Da Dong Bo {len(synced)} lenh slash.")
    except Exception as e:
        print(f"Loi Dong Bo: {e}")

# --- @.@ ---
if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise RuntimeError("Thiếu DISCORD_TOKEN")

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise RuntimeError("Thiếu DISCORD_TOKEN")

    bot.run(token)
