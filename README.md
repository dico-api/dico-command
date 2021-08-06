# dico-command
Command handler for dico.  
**Note: Development of this project will be slow.**

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
Note that using async is forced unlike dico itself.
