# Bots for discord API handler for Python

This is an api handler that I made for the Bots for Discord (Bot list)

# Install

To use this you can install it using pip:</br>
`pip install botsfordiscordapi`

# Example usage

```py
import botsfordiscordapi

#Authorize
## API Version is currently 'v1' but may update in the future

bfd = botsfordiscordapi.login(token, api_version)

#Push server count (Requires token)

bfd.push(bot_id, server_count)

#Get a bot on the list (If it exists)

bfd.get(bot_id)

```

# Example Responses

### GET Response:
```json
{
    "approved": false,
    "avatar": "",
    "count": 1000000, // Server count
    "id": "",
    "invite": "",
    "longDesc": "",
    "name": "",
    "owner": "",
    "ownername": "",
    "ownernametwo": "",
    "prefix": "",
    "shortDesc": "",
    "theme": "",
    "timestamp": ,
    "type": "",
    "verified": false,
    "verifyqueue": false,
    "website": ""
}
```