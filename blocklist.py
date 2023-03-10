from discord.ext import commands, tasks
from datetime import datetime
from pd import pd


keys = ['initial pilot name',
    'known aliases',
    'pilot tag number',
    'known corps/ alliances',
    'reason for being added',
    'corp/alliance of pilot adding them'
]

def setup(bot):
    l = blocklist_cog(bot)
    bot.add_cog(l)

class blocklist_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.d = pd('blocklist.json')
        print('blocklist module loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        mention = f'<@{self.bot.user.id}> '
        if not message.content.startswith(mention):
            return
        msg = message.content[len(mention):].split('\n')
        c = message.channel
        if not msg[0].startswith('blocklist '):
            return
        msg[0] = msg[0][len('blocklist '):]
        if msg[0] == 'show':
            m = 'blocklist:\n' + '\n'.join(self.d.keys())
        elif msg[0].startswith('search '):
            m = f'searching through blacklist for {key}\n'
            k = None
            key = msg[0][len('search '):]
            if key in self.d:
                k = key
            else:
                for i in self.d:
                    if key in self.d[i]['initial pilot name'] or self.d[i]['known aliases']:
                        k = i
                        break
            if k:
                m += '\n'.join([f'{k}: {v}' for k, v in self.d[k].items()])
            else:
                m += 'not found'
        elif msg[0].startswith('add'):
            msg = msg[1:]
            d = {}
            missing = []
            for i in keys:
                for j in msg:
                    if j.startswith(i + ':'):
                        t = j[len(i + ':'):]
                        if t[0] == ' ':
                            t = t[1:]
                        d[i] = t
                if i not in d:
                    missing.append(i)
            if len(missing) > 0:
                m = f'please, provide info in the following format:\n'
                m += '```\n' + '\n'.join([x + ': <text>' for x in keys]) + '```'
                m += f'missing keys: {missing}\n'
            else:
                k = d['pilot tag number']
                if k in self.d:
                    m = 'tag number already blacklisted'
                else:
                    self.d[k] = d
                    self.d.sync()
                    d['date of addition'] = datetime.now().strftime('%Y-%M-%d')
                    a = message.author
                    d['who added'] = f'{str(a)} aka {a.display_name} id {a.id}'
                    m = 'adding this to blacklist:\n```\n'
                    m += '\n'.join([f'{k}: {v}' for k, v in d.items()]) + '```'
        else:
            m = f'invalid command string: {msg[0]}'
        await self.bot.send(c, m)

