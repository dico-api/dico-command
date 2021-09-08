# dico-command
Command handler for dico.  
**Note: Docs is still not ready.**

## Example

```py
import dico
import dico_command

bot = dico_command.Bot("YOUR_TOKEN_HERE", "!", intents=dico.Intents.full())


@bot.command("test")
async def test(ctx: dico_command.Context):
    await ctx.send("Hello, World!")


bot.run()
```

### Using Addon/module:

main.py:
```py
import dico
import dico_command

bot = dico_command.Bot("YOUR_TOKEN_HERE", "!", intents=dico.Intents.full())
bot.load_module("addons.test")
bot.run()
```

addons/test.py:
```py
import dico_command


class AddonTest(dico_command.Addon, name="Addon Test"):  # name=... is optional
    @dico_command.command(name="addon")
    async def example(self, ctx: dico_command.Context):
        await ctx.send(f"Hello! This is addon `{self.name}`.")


def load(bot):
    # Implementing function `load` is required. You may do any actions here.
    bot.load_addons(AddonTest)


def unload(bot):
    # Implementing function `unload` is required. You may do any actions here.
    bot.unload_addons(AddonTest)

```

Note that using async is forced unlike dico itself.
