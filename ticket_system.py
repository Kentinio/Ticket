import disnake
from disnake import ButtonStyle
from disnake.ext import commands
import sqlite3
import os

modlist = []

class clb(disnake.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(label="Удалить тикет", style=ButtonStyle.danger, emoji='<:ticketbutton:933130024356302898>', custom_id="delete_ticket")
    async def delete_ticket(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author.id in modlist:
            con = sqlite3.connect('LastEmpires.db')
            cur = con.cursor()
            cur.execute(f'''DELETE FROM tickets WHERE id_channel = {interaction.channel.id}''')
            await interaction.channel.delete()
            con.commit()
            con.close()
        else:
            await interaction.send("Вы не можете закрыть тикет, ожидайте администратора", ephemeral=True)

    @disnake.ui.button(label="Закрыть тикет", style=ButtonStyle.primary, emoji='<:ticketbutton:933130024356302898>', custom_id="close_ticket")
    async def close_ticket(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author.id in modlist:
            con = sqlite3.connect('LastEmpires.db')
            cur = con.cursor()
            a = cur.execute(f'''SELECT id_member FROM tickets WHERE id_channel = {interaction.channel.id}''').fetchone()
            cur.execute(f'''DELETE FROM tickets WHERE id_channel = {interaction.channel.id}''')
            con.commit()
            con.close()
            try:
                member = await interaction.guild.fetch_member(a[0])
                overwrites = {
                    interaction.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                    member: disnake.PermissionOverwrite(view_channel=False)
                }
                await interaction.channel.edit(category=self.bot.get_channel(964140519867420792).category, overwrites=overwrites)
                await interaction.send("Тикет закрыт.")
                await interaction.message.delete()
                async for message in interaction.channel.history():
                    log = open(f'ticketlog\{a[0]}.txt', 'a', encoding='utf8')
                    log.write(f"Автор: {message.author}({message.author.id}), Сообщение: {message.content}\n")
                    log.close()
                await interaction.send(file=disnake.File(f"ticketlog\{a[0]}.txt"))
                try:
                    await member.send("Транскярипция тикета.", file=disnake.File(f"ticketlog\{a[0]}.txt"))
                except:
                    await interaction.send(f"Нам не получилось отправить транскрипцию {member.mention}({member.name})")
                os.remove(f"ticketlog\{a[0]}.txt")
            except Exception as e:
                await interaction.send("Человек ливнул" + str(e))
        else:
            await interaction.send("Вы не можете закрыть тикет, ожидайте администратора", ephemeral=True)


class ticket_buttons(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Открыть тикет", style=ButtonStyle.primary, emoji='<:ticketbutton:933130024356302898>', custom_id="open_ticket")
    async def open_ticket(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        con = sqlite3.connect('LastEmpires.db')
        cur = con.cursor()
        a1 = cur.execute(f"SELECT id_member FROM tickets WHERE id_member = {interaction.author.id}").fetchone()
        if a1 is None:
            guild = interaction.guild
            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                interaction.author: disnake.PermissionOverwrite(view_channel=True)
            }
            ticket_channel = await guild.create_text_channel(name=f"Тикет-{interaction.author.name}".replace(" ", "_"),
                                                             category=self.bot.get_channel(964140396118687764).category,
                                                             overwrites=overwrites)
            cur.execute(f'''INSERT INTO tickets VALUES ({interaction.author.id}, {ticket_channel.id})''')
            ticket_embed = disnake.Embed(title="Поддержка", colour=0x2F3136, description=f"Здравствуйте, {interaction.author.mention}({interaction.author.name}), чтобы помочь вам, нам нужно как можно четче узнать проблему, не каких форм нет, просто напишите развернуто вопрос или претензию.\n\n"
                                                                              "*Ожидание администратора может занять любое время, но обычно это 10-15 минут*")
            await ticket_channel.send(embed=ticket_embed, view=clb(bot=self.bot))
            await interaction.send(f"Ваш тикет: {ticket_channel.mention}", ephemeral=True)
        else:
            channel1 = cur.execute(f"SELECT id_channel FROM tickets WHERE id_member = {interaction.author.id}").fetchone()
            await interaction.send(f"У вас уже есть тикет - <#{channel1[0]}>, будьте терпиливее, ожидайте администрацию.", ephemeral=True)
        con.commit()
        con.close()


class ticket_system(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.Cog.listener()
    async def on_member_remove(self, member:disnake.Member):
        con = sqlite3.connect('LastEmpires.db')
        cur = con.cursor()
        check = cur.execute(f"SELECT id_member FROM tickets WHERE id_member = {member.id}").fetchone()
        if check is None:
            pass
        else:
            check1 = cur.execute(f"SELECT id_channel FROM tickets WHERE id_member = {check[0]}").fetchone()
            cur.execute(f'''DELETE FROM tickets WHERE id_member = {member.id}''')
            channel = self.bot.get_channel(check1[0])
            await channel.send(f"{member.name}, покинул сервер, <@403829627753070603>")
        con.commit()
        con.close()

    @commands.has_any_role(866948168754659348)
    @commands.command()
    async def tstart(self, ctx):
        con = sqlite3.connect('LastEmpires.db')
        cur = con.cursor()
        cur.execute('''CREATE TABLE tickets (id_member INT, id_channel INT)''')
        con.commit()
        con.close()
        tstartembed = disnake.Embed(title="Успех", colour=0x2F3136, description="Тикет бот успешно установлен, создана таблица для работы, осталось отправить сообщение от тикетов ``*ticket``")
        await ctx.send(embed=tstartembed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.bot.add_view(ticket_buttons(bot=self.bot))
            self.bot.add_view(clb(bot=self.bot))
            self.persistent_views_added = True

    @commands.has_any_role(866948168754659348)
    @commands.command()
    async def ticket(self, ctx):
        ticket_embed = disnake.Embed(title="Поддержка", colour=0x2F3136, description=f"Здравствуйте игрок, что бы открыть тикет нажмите на кнопку ниже.")
        await ctx.send(embed=ticket_embed, view=ticket_buttons(bot=self.bot))


def setup(bot):
    bot.add_cog(ticket_system(bot))