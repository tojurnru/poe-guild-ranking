# POE Guild Ranking (Delve)

Post our guild member delve rankings to Discord. Only members who are in the top 15000 will be shown.

![Sample Discord Message](/readme/ranking.png)

## Environment Variables

Set your environment variables into file `.env` and put them in the same directory

- `DISCORD_WEBHOOK_ID` - 18 digit value that can be obtained from the webhook URL
- `DISCORD_WEBHOOK_HASH` - 68 alphanumeric characters that can be obtained from the webhook URL
- `GUILD_ID` - 6 digit value that can be obtained from your guild profile page
- `POESESSID` - This is required to get guild members from your guild profile page. It's your POE Session ID that is stored in Cookie (google how to get it)

URL Reference:
- `https://discord.com/api/webhooks/{DISCORD_WEBHOOK_ID}/{DISCORD_WEBHOOK_HASH}`
- `https://www.pathofexile.com/guild/profile/{GUILD_ID}`

## Execute

```
python main.py
```
