# urban-async
_A simple async Python wrapper for Urban Dictionary_

# Installation
Run this in your CMD/Terminal:
```
pip3 install urban-async
```

# Updating
Run this in your CMD/Terminal:
```
pip3 install -U urban-async
```

# Usage
Here's an example of how you're supposed to use this:
```py
import urbanasync, asyncio

urbanclient = urbanasync.Client()
term = urbanclient.get_term("")