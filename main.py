import discord
from discord.ext import commands
from colorama import Fore
import youtube_dl
import json

import webserver

with open('config.json','r') as f:
	config = json.load(f)
with open('mycommands.json','r') as f:
  mycommands = json.load(f)

bot = commands.Bot(
  command_prefix=config['prefix'],
  help_command=None
)
color = 0xff0000

@bot.event
async def on_ready():
  print(Fore.GREEN + f"正常に起動しました\nBot:{bot.user}" + Fore.RESET)
  await bot.change_presence(activity=discord.Game(name=f"{config['prefix']}help"))  

@bot.command(name=mycommands['help']['name'],aliases=mycommands['help']['aliases'])
async def help(ctx,info=None):
  p = config['prefix']
  if info == None:
    embed=discord.Embed(title=f"{bot.user.name}のコマンド",description=f"""
    `{p}help` `{p}join` `{p}stop` `{p}play` `{p}pause` `{p}resume`
    """,color=color)
    embed.set_footer(text=f"詳しい使い方は{p}help <コマンド名>で確認できますよ、")
    await ctx.send(embed=embed)
    return
  cmds = bot.get_command(info.lower())    
  if cmds == None:
    await ctx.send(f"コマンドが見つかりませんよ、\n使い方を見る時は{p}を外して検索してください、")
    return
  embed=discord.Embed(title=f"{info}の使い方",color=color)
  embed.add_field(name="コマンド名",value=cmds.name,inline=False)
  embed.add_field(name="エイリアス",value="\n".join(mycommands[cmds.name]['aliases']),inline=False)
  embed.add_field(name="できること",value=mycommands[cmds.name]['usage'],inline=False)
  embed.add_field(name="エイリアスって何？",value=f"エイリアスはこれでも反応するよってことです、\n例でいうと{p}{mycommands['play']['name']}じゃなくて{p}{mycommands['play']['aliases'][0]}でも反応するよってことです、")
  await ctx.send(embed=embed)

@bot.command(name=mycommands['join']['name'],aliases=mycommands['join']['aliases'])
async def join(ctx):
  if ctx.author.voice == None:
    await ctx.send("あなたがボイスチャンネルに参加していませんよ、")
    return 
  if ctx.voice_client == None:
    await ctx.author.voice.channel.connect()
  else:
    await ctx.voice_client.move_to(ctx.author.voice.channel)

@bot.command(name=mycommands['stop']['name'],aliases=mycommands['stop']['aliases'])
async def stop(ctx):
  if ctx.author.voice == None:
    await ctx.send("あなたがボイスチャンネルに参加していませんよ、")
    return
  await ctx.voice_client.disconnect()

@bot.command(name=mycommands['play']['name'],aliases=mycommands['play']['aliases'])
async def play(ctx,*,music=None):
  if ctx.author.voice == None:
    await ctx.send("ボイスチャンネルに参加していません")
    return
  if music == None:
    await ctx.send("曲が指定されていませんよ、")
    return
  if ctx.voice_client == None:
    await ctx.author.voice.channel.connect()
  ctx.voice_client.stop()  
  ffmpeg_option = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  ytdl_option = {'format':'bestaudio','quiet':'true'}
  ytdl = youtube_dl.YoutubeDL(ytdl_option)
  if not "https://" in music or "http://" in music:
    await ctx.send(f"{music}を読み込み中なので少しお待ちください、")
    music = ytdl.extract_info(f"ytsearch:{music}",download=False)['entries'][0]
    sound_source = music['url']
  else:
    await ctx.send(f"<{music}>を読み込み中なので少しお待ちください、")
    music = ytdl.extract_info(music,download=False)
    sound_source = music['formats'][0]['url']
  embed=discord.Embed(title=music['title'],url=music['webpage_url'],color=color)
  embed.set_author(name=music['uploader'])
  embed.set_image(url=music['thumbnail'])
  await ctx.send(embed=embed)
  ctx.voice_client.play(await discord.FFmpegOpusAudio.from_probe(sound_source,**ffmpeg_option))
    
@bot.command(name=mycommands['pause']['name'],aliases=mycommands['pause']['aliases'])
async def pause(ctx):
  if ctx.author.voice == None:
    await ctx.send("あなたがボイスチャンネルに参加していませんよ、")
    return
  ctx.voice_client.pause()
  await ctx.channel.send("曲の再生を一時停止しましたよ、")
    
@bot.command(name=mycommands['resume']['name'],aliases=mycommands['resume']['aliases'])
async def resume(ctx):
  if ctx.author.voice == None:
    await ctx.send("あなたがボイスチャンネルに参加していませんよ、")
    return
  ctx.voice_client.resume()
  await ctx.channel.send("曲の再生を再開しましたよ、")

webserver.start()
bot.run(config['token'])