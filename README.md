# dicomman
Command handler for dico.  
**Note: Development of this project will be slow.**

## Example
```py
import dico
import dicomman

bot = dicomman.Bot("YOUR_TOKEN_HERE", "!", intents=dico.Intents.full())


@bot.command("test")
async def test(ctx: dicomman.Context):
    await ctx.send("Hello, World!")

bot.run()
```