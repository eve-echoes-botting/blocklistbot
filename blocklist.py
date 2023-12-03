from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime
from pd import pd
import os


keys = ['pilot name',
    'pilot id',
    'reason',
]
dkey = 'pilot id'
jistkey = 'pilot name'
searchkey = 'pilot name'

full_access_role_id = 1121764876495376405
yes_no_access_role_id = 1145953261757677598

async def setup(bot):
    l = blocklist_cog(bot)
    await bot.add_cog(l)

class blocklist_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.d = pd('blocklist.json')
        print('blocklist module loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        c = message.channel
        u = message.author
        access = None
        if u.id == 139179662369751041:
            assess = 'full'
        for i in u.roles:
            if i.id == full_access_role_id:
                access = 'full'
                break
            if i.id == yes_no_access_role_id:
                access = 'yesno'
        if not access:
            return
        verbose = c.id == 1151028471628312586
        found = False
        txt = message.content
        ar = [f'<@{self.bot.user.id}> ', f'<@{139179662369751041}>']
        for mention in ar:
            if message.content.startswith(mention):
                msg = message.content[len(mention):]
                found = True
                break
        if verbose:
            await c.send(f'{found} `mention check: {txt} {ar}`')
        if not found:
            return
        if msg.replace(' ', '') == 'blocklist':
            with open(os.path.dirname(os.path.realpath(__file__)) + '/' + 'Readme.md', 'r') as f:
                await c.send(f.read())
                return
        msg = msg.split('\n')
        if not msg[0].startswith('blocklist '):
            return
        msg[0] = msg[0][len('blocklist '):]
        if msg[0] == 'show':
            m = 'blocklist:\n' + '\n'.join([f'`{v[jistkey]}``' for k, v in self.d.items()])
        elif msg[0].startswith('search '):
            found = False
            k = []
            key = msg[0][len('search '):]
            m = f'searching through blocklist for {key}\n'
            if key in self.d:
                k.append(key)
            else:
                for i in self.d:
                    if key == self.d[i][searchkey]:
                        k.append(i)
            if k:
                found = True
                for i in k:
                    m += '\n'.join([f'{ka}: {v}' for ka, v in self.d[i].items()]) + '\n\n'
            else:
                m += 'not found'
        elif msg[0].startswith('add'):
            m = ''
            msg = msg[1:]
            loops = 0
            while msg and loops < 1000:
                d = {}
                missing = []
                fields = msg[:len(keys)]
                print(fields)
                msg = msg[len(keys):]
                for i in keys:
                    for j in fields:
                        if j.startswith(i + ':'):
                            t = j[len(i + ':'):]
                            if t[0] == ' ':
                                t = t[1:]
                            d[i] = t
                    if i not in d:
                        missing.append(i)
                if len(missing) > 0:
                    m += f'please, provide info in the following format. yes, exactly this format:\n'
                    m += '```\n' + '\n'.join([x + ': <text>' for x in keys]) + '```'
                    m += f'missing keys: {missing}\n'
                else:
                    k = d[dkey]
                    if k in self.d:
                        m += f'tag number already blacklisted: {k}\n'
                    else:
                        self.d[k] = d
                        d['date added'] = datetime.now().strftime('%Y-%m-%d')
                        a = message.author
                        d['added by discord member'] = f'{str(a.name)} aka {a.display_name} id {a.id}'
                        self.d.sync()
                        m += 'adding this to blacklist:\n```\n'
                        m += '\n'.join([f'{k}: {v}' for k, v in d.items()]) + '```\n'
                if msg:
                    loops += 1
                    while not msg[0].startswith(keys[0]) and loops < 1000:
                        msg = msg[1:]
                        loops += 1
        else:
            m = f'invalid command string: {msg[0]}'
        if access == 'full':
            await self.bot.send(c, m)
        elif access == 'yesno':
            if found:
                await c.send('yes')
            else:
                await c.send('no')

